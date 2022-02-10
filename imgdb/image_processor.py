from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display
from wand.font import Font
import click
from utils import Tcolors
import textwrap
import logging
from importlib.resources import files
import resources.images as img_dir


def generate_media_image(
    movie_title,
    imdb_rating,
    rt_rating,
    poster_filename,
    poster_filepath,
):

    if poster_filename:
        saved_image_filename = poster_filename + "_by_imgdb"
    else:
        click.echo(
            Tcolors.WARNING + "Downloaded image filename cannot be null!" + Tcolors.ENDC
        )
        logging.critical("Downloaded image filename cannot be null!")
        return

    try:
        float(imdb_rating)
    except (ValueError, TypeError):
        imdb_is_rating_float = False
    else:
        imdb_is_rating_float = True
        imdb_rating_to_perc = (
            imdb_rating if isinstance(imdb_rating, float) else float(imdb_rating)
        ) * 10

    try:
        float(rt_rating)
    except (ValueError, TypeError):
        rt_is_rating_int = False
    else:
        rt_is_rating_int = True
        rt_rating_to_int = rt_rating if isinstance(rt_rating, int) else int(rt_rating)

    if not imdb_is_rating_float and not rt_is_rating_int:
        click.echo(
            Tcolors.WARNING + "Cannot produce picture without ratings!" + Tcolors.ENDC
        )
        logging.critical("Cannot produce picture without ratings!")
        return

    else:
        if imdb_is_rating_float:
            imdb_rounded_rating = round_ratings(imdb_rating_to_perc)
            logging.debug("IMDb's rounded rating is: %s" % imdb_rounded_rating)
        if rt_is_rating_int:
            rt_rounded_rating = round_ratings(rt_rating_to_int)
            logging.debug("RT's rounded rating is: %s" % rt_rounded_rating)

    # Image processing
    with Image(width=800, height=800, background="#3D3737") as canvas:
        with Drawing() as context:
            # Poster image
            with Image(filename=poster_filepath) as poster:
                poster_width = 380
                poster.transform(resize=f"{poster_width}x")
                while poster.height > 570:
                    poster_width -= 5
                    poster.transform(resize=f"{poster_width}x")
                logging.debug("Poster's final height %s" % poster.height)
                canvas.composite(poster, left=40, top=180)

            # Ring charts
            ## Charts' parameters
            ring_size = 140
            x_ring_chart = 460
            y_imdb_rating = 200
            y_rt_rating = 440
            x_rating_text_offset = 130
            y_rating_text_offset = 170
            x_shadow_text_offset = 7
            y_shadow_text_offset = 7

            ## IMDb ring chart rating
            if imdb_is_rating_float:
                imdb_rating_img = files(img_dir).joinpath(
                    f"imdb_{imdb_rounded_rating}.png"
                )
                with Image(filename=imdb_rating_img) as img_imdb:
                    img_imdb.resize(ring_size, ring_size)
                    canvas.composite(img_imdb, left=x_ring_chart, top=y_imdb_rating)

            ## RT ring chart rating
            if rt_is_rating_int:
                rt_rating_img = files(img_dir).joinpath(f"rt_{rt_rounded_rating}.png")
                with Image(filename=rt_rating_img) as img_rt:
                    img_rt.resize(ring_size, ring_size)
                    canvas.composite(img_rt, left=x_ring_chart, top=y_rt_rating)

            # Text
            x_title_text = 25
            x_shadow_title_offset = 5
            y_shadow_title_offset = 5
            fontsize_title = 50
            fontsize_ratings = 70
            # context.font = "Mosk-Ultra-Bold-900"
            context.font = "Maler-Regular"

            header_text = textwrap.fill(movie_title, width=15)
            font_metrics = context.get_font_metrics(
                canvas, header_text.upper(), multiline=True
            )
            logging.debug("Initial font metrics: %s" % str(font_metrics))

            while font_metrics.text_width > 600 or font_metrics.text_height > 150:
                context.font_size -= 1
                font_metrics = context.get_font_metrics(
                    canvas, header_text.upper(), multiline=True
                )
            else:
                while font_metrics.text_width < 600 and font_metrics.text_height < 150:
                    context.font_size += 1
                    font_metrics = context.get_font_metrics(
                        canvas, header_text.upper(), multiline=True
                    )
            logging.debug("Corrected font metrics: %s" % str(font_metrics))

            y_title = int(
                ((180 - font_metrics.text_height) / 2) + font_metrics.character_height
            )
            logging.debug("Title's y-axis value: %s" % y_title)
            context.push()

            ## Text shadow
            context.fill_color = Color("rgba(29, 29, 29, 0.87)")
            context.text(
                x=x_title_text + x_shadow_title_offset,
                y=y_title + y_shadow_title_offset,
                body=header_text.upper(),
            )
            context.font_size = fontsize_ratings
            if imdb_is_rating_float:
                context.text(
                    x=x_ring_chart + x_rating_text_offset + x_shadow_text_offset,
                    y=y_imdb_rating + y_rating_text_offset + y_shadow_text_offset,
                    body=str(imdb_rating),
                )
            if rt_is_rating_int:
                context.text(
                    x=x_ring_chart + x_rating_text_offset + x_shadow_text_offset,
                    y=y_rt_rating + y_rating_text_offset + y_shadow_text_offset,
                    body=str(rt_rating) + "%",
                )

            ## Main text
            context.pop()
            context.fill_color = Color("white")
            context.text(x=x_title_text, y=y_title, body=header_text.upper())
            context.font_size = fontsize_ratings
            if imdb_is_rating_float:
                context.text(
                    x=x_ring_chart + x_rating_text_offset,
                    y=y_imdb_rating + y_rating_text_offset,
                    body=str(imdb_rating),
                )
            if rt_is_rating_int:
                context.text(
                    x=x_ring_chart + x_rating_text_offset,
                    y=y_rt_rating + y_rating_text_offset,
                    body=str(rt_rating) + "%",
                )

            # Text stroke (Obsolete)
            # context.fill_color = Color("transparent")
            # context.stroke_color = Color("rgba(29, 29, 29, 0.87)")
            # context.stroke_width = 1
            # context.text(x=21, y=75, body=movie_title.upper())
            # context.font_size = fontsize_ratings
            # if imdb_is_rating_float:
            #     context.text(x=485, y=290, body=str(imdb_rating))
            # if rt_is_rating_int:
            #     context.text(x=485, y=510, body=str(rt_rating) + "%")

            context(canvas)
            canvas.format = "png"
            display(canvas)
        canvas.save(filename=f"{saved_image_filename}.png")
        logging.info("Edited image saved as: %s" % f"{saved_image_filename}.png")
        click.echo(
            Tcolors.OK_GREEN
            + "Edited image saved as: %s" % f"{saved_image_filename}.png"
            + Tcolors.ENDC
        )


def round_ratings(rating):
    """This functions takes in a movie rating as an argument and returns its corresponding rounded value
    that can be used to choose the correct ring chart picture."""

    rating_steps = [0, 5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 100]
    for step in rating_steps:
        if rating in rating_steps:
            rounded_rating_value = rating_steps[rating_steps.index(rating)]
            break
        # Using zero or 100 only when the rating exactly matches those values.
        # In other words, we don't round values like 2 or 98 for example to zero or 100 respectively!
        elif rating in range(1, 3):
            rounded_rating_value = 5
            break
        elif rating in range(98, 100):
            rounded_rating_value = 95
            break
        else:
            rating_diff = rating - step
            rating_diff_abs = abs(rating_diff)

            if (
                rating in range(3, 10)
                or rating in range(21, 30)
                or rating in range(71, 80)
                or rating in range(91, 100)
            ):
                difference_threshold = 2.5
            else:
                difference_threshold = 5
                rounding_increment = 10

            if rating_diff_abs < difference_threshold:
                rounded_rating_value = step
                break
            elif (
                rating_diff_abs == difference_threshold and difference_threshold != 2.5
            ):
                rounded_rating_value = step + rounding_increment
                break

    if rounded_rating_value is not None:
        logging.debug("Rounded rating value is: %s" % rounded_rating_value)
        return rounded_rating_value


if __name__ == "__main__":
    generate_media_image(
        movie_title="The forever purge",
        imdb_rating="5.4",
        rt_rating=50,
        poster_filename="The forever purge",
        poster_filepath="Meander.jpg",
    )

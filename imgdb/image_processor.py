from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display
from wand.font import Font


def movie_image(
    movie_title=None,
    imdb_rating=None,
    rt_rating=None,
    poster_filename=None,
    poster_filepath=None,
):

    with Image(width=660, height=600, background="#3D3737") as canvas:
        with Drawing() as context:
            fontsize_title = 50
            fontsize_ratings = 70
            context.font = "Mosk-Ultra-Bold-900"

            context.font_size = fontsize_title
            context.fill_color = Color("rgba(29, 29, 29, 0.87)")
            context.text(x=32, y=82, body=movie_title.upper())
            context.font_size = fontsize_ratings
            context.text(x=497, y=297, body=imdb_rating)
            context.text(x=497, y=517, body=rt_rating)
            context.fill_color = Color("white")
            context.font_size = fontsize_title
            context.text(x=25, y=75, body=movie_title.upper())
            context.font_size = fontsize_ratings
            context.text(x=490, y=290, body=imdb_rating)
            context.text(x=490, y=510, body=rt_rating)
            context.fill_color = Color("transparent")
            context.stroke_color = Color("rgba(29, 29, 29, 0.87)")
            context.stroke_width = 1
            context.font_size = fontsize_title
            context.text(x=21, y=75, body=movie_title.upper())
            context.font_size = fontsize_ratings
            context.text(x=485, y=290, body=imdb_rating)
            context.text(x=485, y=510, body=rt_rating)

            with Image(filename=poster_filepath) as poster:
                poster.transform(resize="300x ")
                canvas.composite(poster, left=40, top=100)

            with Image(filename="./art/imdb_10.png") as img_imdb:
                img_imdb.resize(140, 140)
                canvas.composite(img_imdb, left=360, top=120)

            with Image(filename="./art/rt_60.png") as img_rt:
                img_rt.resize(140, 140)
                canvas.composite(img_rt, left=360, top=340)

            context(canvas)
            canvas.format = "png"
            display(canvas)
        # canvas.save(filename="font_shadow.png")


if __name__ == "__main__":
    movie_image(
        movie_title="The Dark Knight Rises",
        imdb_rating="8.4",
        rt_rating="89.3",
        poster_filepath="The_Dark_Knight_Rises.jpg",
    )

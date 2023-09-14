import os
from pathlib import Path

import typer
from PIL import Image
from rembg import remove

app = typer.Typer()


class TokenGenerator:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.file_name = Path(input_path).stem
        self.path = Path(input_path).parent

    def _remove_background(self):
        outputted_file_path = Path(self.input_path).with_name(
            f'{Path(self.input_path).stem}-removed.png'
        )

        image = Image.open(self.input_path)
        image_bg_removed = remove(image)
        image_bg_removed.save(outputted_file_path, 'PNG')

        return image_bg_removed

    def _add_token_to_image(self, image_bg_removed: Image):
        border = Image.open(f'{os.getcwd()}/token_generator/border.png')

        image_bg_removed_resized = image_bg_removed.resize((250, 250))
        image_bg_removed_resized.save(f'{self.path}/{self.file_name}-resized.png', 'PNG')

        resized = Image.open(f'{self.path}/{self.file_name}-resized.png')

        background = resized.convert('RGBA')
        overlay = border.convert('RGBA')

        background.paste(overlay, (0, 0), mask=overlay)
        background.save(f'{self.path}/{self.file_name}-token.png', 'PNG')

        return background

    def _clean_files(self):
        Path(f'{self.path}/{self.file_name}-resized.png').unlink()
        Path(f'{self.path}/{self.file_name}-removed.png').unlink()

    def create_token(self):
        print('Criando token...')
        image_bg_removed = self._remove_background()
        token = self._add_token_to_image(image_bg_removed)
        self._clean_files()

        print('Ok' if token else 'Erro')
        print('Token criado com sucesso!')


@app.command()
def main(input_path: str):
    TokenGenerator(input_path).create_token()

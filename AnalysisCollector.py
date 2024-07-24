import asyncio
import json
import nbformat
from nbclient.exceptions import CellExecutionError
from nbconvert import HTMLExporter
import aiofiles
import os
from nbconvert.preprocessors import ExecutePreprocessor

NOTEBOOK_PATH = 'political_review_display.ipynb'


async def get_film_html(id_imdb, force_update=False, verbose=True):
    film_path = f'Data/{id_imdb}/{id_imdb}_analysis.html'
    if os.path.exists(film_path) and not force_update:
        if verbose:
            print("Retrieving analysis data from local storage")
        async with aiofiles.open(film_path, 'r') as file:
            film_data = await file.read()
        return film_data
    else:
        directory = f'Data/{id_imdb}'
        os.makedirs(directory, exist_ok=True)
        html_content = await run_notebook_and_save_html(directory, id_imdb)
        if html_content:
            return html_content
        else:
            print("Failed to run the notebook")
            return None


async def run_notebook_and_save_html(output_html_path, imdb_id):
    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as file:
        nb = nbformat.read(file, as_version=4)

    if len(nb.cells) > 1:
        nb.cells[1].source = f"FILM_ID = '{imdb_id}'  # This sets the FILM_ID"

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    try:
        ep.preprocess(nb, {'metadata': {'path': './'}})
    except CellExecutionError as ex:
        print("Error executing the notebook:", str(ex))
        print("Traceback:", ex.traceback)
        return
    except Exception as e:
        print("General error while executing the notebook:", str(e))
        return

    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'
    html_exporter.exclude_input = True

    (body, _) = html_exporter.from_notebook_node(nb)

    async with aiofiles.open(output_html_path + f'/{imdb_id}_analysis.html', 'w', encoding='utf-8') as file:
        await file.write(body)

    print("Notebook has been processed, analysis is ready.")
    return body


def find_html_and_extract_data():
    result = []

    for root, dirs, files in os.walk("Data"):
        if any(file.endswith('.html') for file in files):
            folder_name = os.path.basename(root)
            json_filename = f"{folder_name}_film.json"
            json_path = os.path.join(root, json_filename)
            if os.path.exists(json_path):
                with open(json_path, 'r') as json_file:
                    data = json.load(json_file)
                    name = data.get('name')
                    ID = folder_name
                    result.append({'label': name, 'value': ID})

    return result


if __name__ == '__main__':
    asyncio.run(get_film_html(id_imdb='tt0286716', force_update=True, verbose=True))

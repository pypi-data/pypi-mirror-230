import os
import tempfile
import concurrent.futures
import pandas as pd
from pathlib import Path
from pdf2image import pdfinfo_from_bytes, convert_from_bytes
from tqdm import tqdm
from toolz import curry


def extract_page_text(page, f, temp_dir):
    image_path = temp_dir / f'page{page}.jpg'
    page_path = temp_dir / f'page{page}.tsv'
    image = convert_from_bytes(f, dpi=300, userpw=None, poppler_path=None, first_page=page, last_page=page)[0]
    image.save(image_path, 'JPEG')
    cmd = f'tesseract --oem 2 {image_path} {page_path.parent / page_path.stem} tsv'
    os.system(cmd)
    page_data = pd.read_csv(page_path, sep='\t', quoting=3)
    page_data = page_data[(page_data['conf'] >= 0) & page_data['text'].notnull()]
    page_data = page_data.groupby(['page_num', 'block_num']).agg({'text': ' '.join, 'conf': 'mean'}).reset_index()
    page_data['page'] = page
    page_data = page_data.rename(columns={'block_num': 'chunk'}).drop(columns=['page_num'])
    return page_data.to_dict('records')


def ocr_pdf(f, page=None, workers=1):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        if page is None:
            info = pdfinfo_from_bytes(f, userpw=None)
            pages = list(range(1, info['Pages'] + 1))
        else:
            pages = [page]

        mapper = curry(extract_page_text, f=f, temp_dir=temp_dir)
        with concurrent.futures.ThreadPoolExecutor(workers) as executor:
            data = list(tqdm(executor.map(mapper, pages), total=len(pages)))
        data = [x for y in data for x in y]
        return data



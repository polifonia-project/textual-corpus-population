import argparse
import ntpath
import os
import re

import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv

load_dotenv()
Image.MAX_IMAGE_PIXELS = 933120000
SUPPORTED_IMAGE_FORMAT = ['.png', '.jpg', '.jpeg', '.tiff', '.gif']


def file_info(file_path):
    """Takes as input the file input path and the output path and analyses the file name and the file extension.
    It also set a destination folder for the conversion from pdf to image."""
    if file_path == "" or file_path is None:
        raise NameError("Directories Not Set")
    elif os.path.isdir(file_path):
        file_ext = None
        file_name_no_ext = ntpath.basename(file_path)
    else:
        file_name = ntpath.basename(file_path)
        file_name_no_ext = os.path.splitext(file_name)[0]
        file_ext = os.path.splitext(file_name)[1]

    return file_name_no_ext, file_ext


def convert_image(file_path, out_path, out_format="png"):
    image = Image.open(file_path)
    out_path = f"{out_path}/{file_path.split('/')[-1].split('.')[0]}.{out_format}"
    image.save(out_path)


def pdf_to_img(file_path, final_path, out_format='png'):
    file_name_no_ext, file_ext = file_info(file_path)
    results_path = f'{final_path}/{file_name_no_ext}'
    print(file_path)
    # check if exists a folder with the same name of the input file. If not, create one.
    if not os.path.isdir(results_path):
        os.makedirs(results_path)
    else:
        pass
    pages = convert_from_path(file_path, 500)

    page_num = 0
    for page in pages:
        page_num += 1
        print(f'SAVING PAGE: {page_num}')
        page.save(f'{results_path}/{page_num}.{out_format}', out_format)
    print(results_path)
    return results_path


def image_processing(input_path, gray_scale, remove_noise, thresholding, dilate, erosion, edge_detection,
                     skew_correction, see_image):
    print(input_path, gray_scale, remove_noise, thresholding, dilate, erosion, edge_detection,
                     skew_correction, see_image)
    kernel = np.ones((5, 5), np.uint8)
    image = cv2.imread(input_path)

    if gray_scale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if remove_noise:
        image = cv2.medianBlur(image, 5)
    if thresholding:
        image = cv2.threshold(image, 125, 255, cv2.THRESH_BINARY)[1]
        # image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,21,4)
    if dilate:
        image = cv2.dilate(image, kernel, iterations=1)
    if erosion:
        image = cv2.erode(image, kernel, iterations=1)
    if edge_detection:
        image = cv2.Canny(image, 100, 200)
    if skew_correction:
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    if see_image:
        cv2.imwrite(f'eval_files/{os.path.basename(input_path)[0]}_show{os.path.splitext(input_path)[1]}', image)
        print('SAVED PROCESSED IMAGE')
    return image


def ocr(processed_image, language_mode, psm, oem, multilang="", language=""):
    if type(psm) != int or not psm:
        raise NameError("PAGE_SEGMENTATION_MODE not set")
    if language_mode == "multi" and multilang != "":
        custom_config = r'-l {} --oem {} --psm {}'.format(multilang, oem, psm)
        ocr_output = pytesseract.image_to_string(processed_image, config=custom_config)
    elif language_mode == "mono" and language != "":
        if not oem:
            raise NameError("OCR_ENGINE_MODE not set")
        custom_config = r'--oem {} --psm {}'.format(oem, psm)
        # custom_config2 = r'--oem 3 --psm 1'
        ocr_output = pytesseract.image_to_string(processed_image, config=custom_config, lang=language)
    else:
        raise NameError("Language Setting Error")
    return ocr_output


def ocrise_folder(folder_path, saved_file_path, output_format):
    ocr_all, ocr_all_pdf = '', ''
    for path, dirs, files in os.walk(folder_path):
        if len(dirs) == 0: #220422_AG: added to avoid multiple iterations over files into nested folders
            for file in sorted(files, key=lambda f: int(re.sub('\D', '1', f))):
                filename, file_extension = os.path.splitext(file)
                if file_extension == '.pdf':
                    # folder created inside the same folder as the input one.
                    print(f'The file {filename} is a .pdf file. Converting to image in {output_format} format.')
                    converted_image_path = pdf_to_img(f'{path}/{file}', folder_path, output_format)
                    ocrise_pdf(converted_image_path, filename, saved_file_path)
                elif file_extension in SUPPORTED_IMAGE_FORMAT:
                    text = ocrise_single(input_file=f'{path}/{file}',
                                         language_mode=args.language_mode,
                                         single_lang=args.single_language,
                                         multiple_langs=args.multiple_langs,
                                         psm=args.page_segmentation_mode,
                                         oem=args.ocr_engine_mode,
                                         gray_scale=args.gray_scale,
                                         remove_noise=args.remove_noise,
                                         thresholding=args.thresholding,
                                         dilate=args.dilate,
                                         erosion=args.erosion,
                                         edge_detection=args.edge_detection,
                                         skew_correction=args.skew_correction,
                                         see_image=args.see_image)
                    if len([x for x in files if '_' in x]) > 0: #220422_AG: added to handle DE periodicals filenames specificities
                        if f"{(path.split('/')[-1])}.txt" not in [f for f in os.listdir(saved_file_path)]:
                            save_to_txt(f"{saved_file_path}/{(path.split('/')[-1])}.txt", text)
                        elif f"{(path.split('/')[-1])}.txt" in [f for f in os.listdir(saved_file_path)]:
                            with open(f"{saved_file_path}/{(path.split('/')[-1])}.txt", "a") as existing_file:
                                existing_file.write(f"\n\n\n{text}")  # print(filename, file_extension)
                    elif len([x for x in files if '-' in x]) > 0 and len(file.split('-')[:-1]) > 1:
                        if f"{'-'.join(file.split('-')[:-1])}.txt" not in [f for f in os.listdir(saved_file_path)]:
                            save_to_txt(f"{saved_file_path}/{'-'.join(file.split('-')[:-1])}.txt", text)
                        elif f"{'-'.join(file.split('-')[:-1])}.txt" in [f for f in os.listdir(saved_file_path)]:
                            with open(f"{saved_file_path}/{'-'.join(file.split('-')[:-1])}.txt", "a") as existing_file:
                                existing_file.write(f"\n\n\n{text}")
                    else:
                        ocr_all = ocr_all + text
                else:
                    print(f'FILE FORMAT NOT SUPPORTED (yet!), SKIPPING {file}')
            if len(ocr_all) > 0:
                save_to_txt(f'{saved_file_path}/{path.split("/")[-1]}.txt', ocr_all)
                print(f'SAVED FILE {saved_file_path}/{path.split("/")[-1]}.txt')
        else:
            pass

def ocrise_pdf(converted_image_path, filename, output_folder):
    ocr_all_pdf = ''
    for path, dirs, files in os.walk(converted_image_path):
        for img in sorted(files, key=lambda f: int(re.sub('\D', '1', f))):
            text = ocrise_single(input_file=f'{path}/{img}',
                                 language_mode=args.language_mode,
                                 single_lang=args.single_language,
                                 multiple_langs=args.multiple_langs,
                                 psm=args.page_segmentation_mode,
                                 oem=args.ocr_engine_mode,
                                 gray_scale=args.gray_scale,
                                 remove_noise=args.remove_noise,
                                 thresholding=args.thresholding,
                                 dilate=args.dilate,
                                 erosion=args.erosion,
                                 edge_detection=args.edge_detection,
                                 skew_correction=args.skew_correction,
                                 see_image=args.see_image)
            ocr_all_pdf = ocr_all_pdf + text
    save_to_txt(f'{output_folder}/{filename}.txt', ocr_all_pdf)


def ocrise_single(input_file, language_mode, single_lang, multiple_langs, psm, oem,
                  gray_scale, remove_noise, thresholding, dilate, erosion, edge_detection, skew_correction, see_image):
    print("PROCESSING IMAGE: {}".format(input_file))

    image = image_processing(input_file, gray_scale, remove_noise, thresholding, dilate, erosion, edge_detection,
                             skew_correction, see_image)
    image_ocr = ocr(image, language_mode, psm, oem, multiple_langs, single_lang)

    return image_ocr


def save_to_txt(out_name: str, ocr_res: str):
    f = open(out_name, 'w')
    f.write(str(ocr_res.encode('utf-8')))
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # File parameters
    parser.add_argument('--input_path',
                        type=str,
                        default=os.getenv('INPUT_PATH'))  # accepts pdf files, image files and image folders
    parser.add_argument('--saved_file_path',
                        type=str,
                        default=os.getenv('OUTPUT_PATH'))  # only needed if the input format is pdf
    parser.add_argument('--converted_image_output_path',
                        type=str,
                        default=os.getenv('CONVERTED_IMAGE_PATH'))  # only needed if the input format is pdf
    parser.add_argument('--output_format',
                        type=str,
                        default=os.getenv('OUTPUT_FORMAT'))  # only needed if the input format is pdf

    # Language parameters
    parser.add_argument('--language_mode',
                        type=str,
                        default=os.getenv('LANGUAGE_MODE'))  # "multi" if working with more tha n one language, "mono" otherwise
    parser.add_argument('--single_language',
                        type=str,
                        default=os.getenv('SINGLE_LANGUAGE'))  # needed if working with --language_mode = "single"
    parser.add_argument('--multiple_langs',
                        type=str,
                        default=os.getenv('MULTIPLE_LANGUAGES'))  # needed if working with --language_mode = "multi"

    # Preprocessing parameters
    parser.add_argument('--gray_scale', type=bool, default=os.getenv('GRAY_SCALE'))
    parser.add_argument('--remove_noise', type=bool, default=os.getenv('REMOVE_NOISE'))
    parser.add_argument('--thresholding', type=bool, default=os.getenv('THRESHOLDING'))
    parser.add_argument('--dilate', type=bool, default=os.getenv('DILATE'))
    parser.add_argument('--erosion', type=bool, default=os.getenv('EROSION'))
    parser.add_argument('--edge_detection', type=bool, default=os.getenv('EDGE_DETECTION'))
    parser.add_argument('--skew_correction', type=bool, default=os.getenv('SKEW_CORRECTION'))
    parser.add_argument('--see_image', type=bool, default=os.getenv('SEE_IMAGE'))

    # OCR parameters
    parser.add_argument('--page_segmentation_mode', type=int, default=os.getenv('PAGE_SEGMENTATION_MODE'))
    parser.add_argument('--ocr_engine_mode', type=int, default=os.getenv('OCR_ENGINE_MODE'))

    args = parser.parse_args()

    print(args.skew_correction, os.getenv('SKEW_CORRECTION'))

    file_name, extension = file_info(args.input_path)
    if extension == ".pdf" and not os.path.isdir(args.input_path):
        print("The input file is a .pdf file. Converting to image in {} format.".format(args.output_format))
        converted_images = pdf_to_img(args.input_path, args.converted_image_output_path, args.output_format)
        ocrise_pdf(converted_images, file_name, args.saved_file_path)
    elif os.path.isdir(args.input_path):
        print("The input corresponds to a folder. Processing files contained in it.")
        ocrise_folder(args.input_path, args.saved_file_path, args.output_format)
    else:
        text = ocrise_single(input_file=args.input_path,
                             language_mode=args.language_mode,
                             single_lang=args.single_language,
                             multiple_langs=args.multiple_langs,
                             psm=args.page_segmentation_mode,
                             oem=args.ocr_engine_mode,
                             gray_scale=args.gray_scale,
                             remove_noise=args.remove_noise,
                             thresholding=args.thresholding,
                             dilate=args.dilate,
                             erosion=args.erosion,
                             edge_detection=args.edge_detection,
                             skew_correction=args.skew_correction,
                             see_image=args.see_image)
        save_to_txt(f'{args.saved_file_path}/{file_name}.txt', text)
        print(f'SAVED FILE {args.saved_file_path}/{file_name}.txt')

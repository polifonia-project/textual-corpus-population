import ntpath
import os
import re

import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

INPUT_PATH = "/Users/andreapoltronieri/Documents/Assegno/Polifonia/WP4/Books/L'arpa"  # accepts pdf files, png files,
# and folders containing multiple png files
OUTPUT_PATH = ""  # only needed if the give input is in .pdf format
OUTPUT_FORMAT = "png"  # only needed if the input file is a pdf and hence needs to be converted
OUTPUT_NAME = "arpa_010.txt"  # name of the output file. It must be a txt file.
LANGUAGE_MODE = "mono"  # set this parameter to "multi" if working with more tha n one language, set "mono" otherwise
LANGUAGE = "ita"  # if working with LANGUAGE_MODE = "single" set this parameter
MULTIPLE_LANG = "fra+eng+ita+spa+deu"  # if working with LANGUAGE_MODE = "multi" set this parameter.
# Languages must be concatenated using the "+" symbol. No spaces required.

# Preprocessing parameters
GRAY_SCALE: bool = True
REMOVE_NOISE: bool = False
TRESHOLDING: bool = False
DILATE: bool = False
EROSION: bool = False
EDGE_DETECTION: bool = False
SKEW_CORRECTION: bool = False

# OCR parameters
PAGE_SEGMENTATION_MODE: int = 6
OCR_ENGINE_MODE: int = 3


def file_info(file_path, out_path):
    """Takes as input the file input path and the output path and analyses the file name and the file extension.
    It also set a destination folder for the conversion from pdf to image."""
    if (file_path == "" or file_path is None) and (out_path == "" or out_path is None):
        raise NameError("Directories Not Set")
    elif os.path.isdir(file_path):
        results_path = file_path
        file_ext = None
        file_name_no_ext = ntpath.basename(file_path)
    elif file_path.endswith(".pdf"):
        file_name = ntpath.basename(file_path)
        file_name_no_ext = os.path.splitext(file_name)[0]
        file_ext = os.path.splitext(file_name)[1]
        results_path = out_path + file_name_no_ext
    elif file_path.endswith(".png"):
        file_name = ntpath.basename(file_path)
        file_name_no_ext = os.path.splitext(file_name)[0]
        file_ext = os.path.splitext(file_name)[1]
        results_path = file_path
    else:
        raise NameError("Input File Format Not Valid")

    return file_name_no_ext, file_ext, results_path


def pdf_to_img(file_path, out_path, out_format="png"):
    file_name_no_ext, file_ext, results_path = file_info(file_path, out_path)
    # check if exists a folder with the same name of the input file. If not, create one.
    if not os.path.isdir(results_path):
        os.makedirs(results_path)
    else:
        pass

    pages = convert_from_path(file_path, 500)

    page_num = 0
    for page in pages:
        page_num += 1
        page.save("{}/{}.{}".format(results_path, page_num, out_format), out_format)
        print("SAVING IMAGE: {}".format(page))


def image_processing(input_path, gray_scale=True, remove_noise=False, tresholding=False, dilate=False, erosion=False,
                     edge_detection=False, skew_correction=False):
    kernel = np.ones((5, 5), np.uint8)
    image = cv2.imread(input_path)

    if gray_scale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if remove_noise:
        image = cv2.medianBlur(image, 5)
    if tresholding:
        image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
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
    return image


def ocr(processed_image, language_mode, oem, psm, multilang="", language=""):
    if not psm:
        raise NameError("PAGE_SEGMENTATION_MODE not set")
    if language_mode == "multi" and multilang != "":
        custom_config = r'-l {} --psm {}'.format(multilang, psm)
        ocr_output = pytesseract.image_to_string(processed_image, config=custom_config)
    elif language_mode == "mono" and language != "":
        if not oem:
            raise NameError("OCR_ENGINE_MODE not set")
        custom_config = r'--oem {} --psm {}'.format(oem, psm)
        ocr_output = pytesseract.image_to_string(processed_image, config=custom_config, lang=language)
    else:
        raise NameError("Language Setting Error")
    return ocr_output


def save_to_txt(out_name, ocr_res):
    f = open(out_name, 'w')
    f.write(ocr_res)
    f.close()


if __name__ == "__main__":
    file_name, extension, final_path = file_info(INPUT_PATH, OUTPUT_PATH)
    if extension == ".pdf" and not os.path.isdir(final_path):
        print("The input file is a .pdf file. Converting to image in {} format.".format(OUTPUT_FORMAT))
        pdf_to_img(INPUT_PATH, OUTPUT_PATH, OUTPUT_FORMAT)
    elif extension == ".png":
        pass
    else:
        print("The input corresponds to a folder. Processing files contained in it.")

    ocr_all = ""

    if extension == ".pdf" or extension is None:
        print("PROCESSING FOLDER: {}".format(final_path))
        for path, dirs, images in os.walk(final_path):
            for image in sorted(images, key=lambda f: int(re.sub('\D', '1', f))):
                filename, file_extension = os.path.splitext(image)
                if file_extension == ".{}".format(OUTPUT_FORMAT):
                    print("PROCESSING IMAGE: {}/{}".format(path, image))

                    image = image_processing("{}/{}".format(path, image), gray_scale=GRAY_SCALE,
                                             remove_noise=REMOVE_NOISE, tresholding=TRESHOLDING, dilate=DILATE,
                                             erosion=EROSION, edge_detection=EDGE_DETECTION,
                                             skew_correction=SKEW_CORRECTION)
                    image_ocr = ocr(image, LANGUAGE_MODE, PAGE_SEGMENTATION_MODE, OCR_ENGINE_MODE,
                                    MULTIPLE_LANG, LANGUAGE)
                else:
                    print("UNABLE TO PROCESS FILE: {}".format(image))
                    continue

                ocr_all = ocr_all + "\n" + image_ocr
    else:
        print("PROCESSING IMAGE: {}".format(final_path))
        print(final_path)
        image = image_processing(final_path, gray_scale=GRAY_SCALE, remove_noise=REMOVE_NOISE,
                                 tresholding=TRESHOLDING, dilate=DILATE, erosion=EROSION,
                                 edge_detection=EDGE_DETECTION, skew_correction=SKEW_CORRECTION)
        image_ocr = ocr(image, LANGUAGE_MODE, PAGE_SEGMENTATION_MODE, OCR_ENGINE_MODE, MULTIPLE_LANG, LANGUAGE)
        ocr_all = image_ocr

    save_to_txt(OUTPUT_NAME, ocr_all)
    print("\nOCR completed.\n\nSaved file as: {}".format(OUTPUT_NAME))

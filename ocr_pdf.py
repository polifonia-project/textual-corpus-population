import ntpath
import os
import re
import argparse

import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

Image.MAX_IMAGE_PIXELS = 933120000


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


def convert_image(file_path, out_path, out_format="png"):
    image = Image.open(file_path)
    out_path = f"{out_path}/{file_path.split('/')[-1].split('.')[0]}.{out_format}"
    image.save(out_path)


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
        print("SAVING PAGE: {}".format(page_num))
        page.save("{}/{}.{}".format(results_path, page_num, out_format), out_format)


def image_processing(input_path, gray_scale=True, remove_noise=False, tresholding=False, dilate=False, erosion=False,
                     edge_detection=False, skew_correction=False):
    kernel = np.ones((5, 5), np.uint8)
    image = cv2.imread(input_path)

    if gray_scale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if remove_noise:
        image = cv2.medianBlur(image, 5)
    if tresholding:
        image = cv2.threshold(image, 125, 255, cv2.THRESH_BINARY)[1]
        # image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_MEAN_C,
        #                               cv2.THRESH_BINARY,21,4)
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
    # plt.imshow(image, 'gray')
    # plt.show()
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
        custom_config2 = r'--oem 3 --psm 1'
        ocr_output = pytesseract.image_to_string(processed_image, config=custom_config, lang=language)
    else:
        raise NameError("Language Setting Error")
    return ocr_output


def ocrise_pdf(final_path, language_mode, single_lang, multiple_langs, output_format='png', psm=1, oem=3):
    ocr_all = ""
    print("PROCESSING FOLDER: {}".format(final_path))
    for path, dirs, images in os.walk(final_path):
        for image in sorted(images, key=lambda f: int(re.sub('\D', '1', f))):
            filename, file_extension = os.path.splitext(image)
            if file_extension == ".{}".format(output_format):
                print("PROCESSING IMAGE: {}/{}".format(path, image))

                processed_image = image_processing("{}/{}".format(path, image))
                image_ocr = ocr(processed_image, language_mode, psm, oem,
                                multiple_langs, single_lang)
                if len(filename.split('-')[:-1]) > 1:
                    if extension is None and f"{'-'.join(filename.split('-')[:-1])}.txt" not in [f for f in
                                                                                                 os.listdir('./')]:
                        save_to_txt(f"{'-'.join(filename.split('-')[:-1])}.txt", image_ocr)
                    elif extension is None and f"{'-'.join(filename.split('-')[:-1])}.txt" in [f for f in
                                                                                               os.listdir('./')]:
                        with open(f"{'-'.join(filename.split('-')[:-1])}.txt", "a") as existing_file:
                            existing_file.write(f"\n\n\n{image_ocr}")
                else:
                    ocr_all = ocr_all + image_ocr
                if extension is not None:
                    ocr_all = ocr_all + image_ocr
            else:
                print("UNABLE TO PROCESS FILE: {}".format(image))
                continue
    return ocr_all


# def ocrise_image():
#     print("PROCESSING IMAGE: {}".format(final_path))
#     print(final_path)
#     image = image_processing(final_path, gray_scale=GRAY_SCALE, remove_noise=REMOVE_NOISE,
#                              tresholding=TRESHOLDING, dilate=DILATE, erosion=EROSION,
#                              edge_detection=EDGE_DETECTION, skew_correction=SKEW_CORRECTION)
#     image_ocr = ocr(image, LANGUAGE_MODE, PAGE_SEGMENTATION_MODE, OCR_ENGINE_MODE, MULTIPLE_LANG, LANGUAGE)
#     return image_ocr


def save_to_txt(out_name, ocr_res):
    f = open(out_name, 'w')
    f.write(ocr_res)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # File parameters
    parser.add_argument('--input_path', type=str,
                        default='/Users/andreapoltronieri/PycharmProjects/ocr/Evo2022_paper_186')  # accepts pdf files, image files and image folders
    parser.add_argument('--output_path', type=str, default='')  # only needed if the input format is pdf
    parser.add_argument('--output_format', type=str, default='png')  # only needed if the input format is pdf
    parser.add_argument('--output_name', type=str, default='test.txt')  # name of the output .txt file

    # Language parameters
    parser.add_argument('--language_mode', type=str,
                        default='mono')  # "multi" if working with more tha n one language, "mono" otherwise
    parser.add_argument('--single_language', type=str,
                        default='eng')  # needed if working with --language_mode = "single"
    parser.add_argument('--multiple_langs', type=str,
                        default='fra+eng+ita+spa+deu')  # needed if working with --language_mode = "multi"

    # Preprocessing parameters
    parser.add_argument('--gray_scale', type=bool, default='True')
    parser.add_argument('--remove_noise', type=bool, default='False')
    parser.add_argument('--tresholding', type=bool, default='True')
    parser.add_argument('--dilate', type=bool, default='False')
    parser.add_argument('--erosion', type=bool, default='False')
    parser.add_argument('--edge_detection', type=bool, default='False')
    parser.add_argument('--skew_correction', type=bool, default='False')

    # OCR parameters
    parser.add_argument('--page_segmentation_mode', type=int, default=1)
    parser.add_argument('--ocr_engine_mode', type=int, default=3)

    args = parser.parse_args()

    file_name, extension, final_path = file_info(args.input_path, args.output_path)
    if extension == ".pdf" and not os.path.isdir(final_path):
        print("The input file is a .pdf file. Converting to image in {} format.".format(args.output_format))
        pdf_to_img(args.input_path, args.output_path, args.output_format)

    elif extension is None:
        print("The input corresponds to a folder. Processing files contained in it.")
        print(final_path)
        args.output_path = final_path
    else:
        pass

    ocr_all = ocrise_pdf(final_path=args.output_path,
                         language_mode=args.language_mode,
                         single_lang=args.single_language,
                         multiple_langs=args.multiple_langs,
                         output_format=args.output_format,
                         psm=args.page_segmentation_mode,
                         oem=args.ocr_engine_mode)

    if len(ocr_all) > 1:
        save_to_txt(args.output_name, ocr_all)
        print("\nOCR completed.\n\nSaved file as: {}".format(args.output_name))

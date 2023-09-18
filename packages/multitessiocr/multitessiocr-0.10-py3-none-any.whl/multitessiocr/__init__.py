import os
import re
import subprocess
import tempfile
from typing import Union

import cv2
import numpy as np
from shortpath83 import get_short_path_name
from a_cv_imwrite_imread_plus import open_image_in_cv
from touchtouch import touch
from a_pandas_ex_xml2df import pd_add_read_xml_files
import pandas as pd
from a_pandas_ex_enumerate_groups import pd_add_enumerate_group

pd_add_enumerate_group()
pd_add_read_xml_files()

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
creationflags = subprocess.CREATE_NO_WINDOW
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
    "start_new_session": True,
}


def try_to_convert_to_int(x):
    try:
        return int(x)
    except:
        return x


def get_tmpfile(suffix=".png"):
    tfp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    filename = tfp.name
    filename = os.path.normpath(filename)
    tfp.close()
    touch(filename)
    return filename


def tesser_ocr(
    tesseract_path: str,
    allpics: Union[list, tuple],
    add_after_tesseract_path: str = "",
    add_at_the_end: str = "-l eng --psm 3",
    **kwargs,
):
    r"""
    Performs OCR on a list of images (file path, url, base64, bytes, numpy, PIL ...) using Tesseract and returns the recognized text,
    its coordinates, and line-based word grouping in a DataFrame.

    This function takes a path to the Tesseract OCR executable, a list of image paths, URLs,
    base64 strings, numpy arrays, bytes or PIL images
    and optional Tesseract command line arguments. It uses Tesseract to extract text from
    the provided images and returns the results as a pandas DataFrame.

    Args:
        tesseract_path (str): The path to the Tesseract OCR executable.
        allpics (list, tuple): A list of images (image paths, URLs, base64 strings, numpy arrays,
                                bytes or PIL images) to be processed.
        add_after_tesseract_path (str, optional): Additional arguments to pass to Tesseract
            after the tesseract executable file path. Defaults to an empty string.
        add_at_the_end (str, optional): Additional arguments to append at the end of the
            Tesseract command. Defaults to '-l eng --psm 3'.
        **kwargs: Additional keyword arguments to control the subprocess execution,
            such as 'stdout', 'stderr', 'timeout', etc. See the 'subprocess.run'
            documentation for more details.

    Returns:
        pandas.DataFrame: A DataFrame containing the OCR results with columns:
            - 'id_img': Image ID (integer)
            - 'id_word': Word ID within the image (integer)
            - 'ocr_result': Recognized text (string)
            - 'start_x': Starting X-coordinate of the bounding box (integer)
            - 'end_x': Ending X-coordinate of the bounding box (integer)
            - 'start_y': Starting Y-coordinate of the bounding box (integer)
            - 'end_y': Ending Y-coordinate of the bounding box (integer)
            - 'conf': Confidence score (integer)
            - 'text_group': Group identifier for enumerated groups (integer)

    Example:
        from multitessiocr import tesser_ocr
        df = tesser_ocr(
            tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            allpics=[
                "https://m.media-amazon.com/images/I/711y6oE2JrL._SL1500_.jpg",
                "https://m.media-amazon.com/images/I/61g+KBpG20L._SL1500_.jpg",
            ],
            add_after_tesseract_path="",
            add_at_the_end="-l eng --psm 3",
        )
        print(df.to_string())
        # ...
        # 11       1       12         today.      402    498      460    492    96       3072       450       476     96      32           4
        # 12       1       13           Wait      551    635      525    556    95       2604       593       540     84      31           5
        # 13       1       14           till      645    695      525    556    96       1550       670       540     50      31           5
        # 14       1       15            you      705    773      533    565    96       2176       739       549     68      32           5
        # 15       1       16           hear      562    645      579    610    95       2573       603       594     83      31           6
        # 16       1       17          about      663    767      579    610    96       3224       715       594    104      31           6
        # 17       2        1            ART       94    246      125    207    95      12464       170       166    152      82           7
        # 18       2        2             OF      275    376      125    207    95       8282       325       166    101      82           7
        # 19       2        3     NONVIOLENT      407    907      125    206    96      40500       657       165    500      81           7
        # 20       2        4  COMMUNICATION      167    832      296    377    96      53865       499       336    665      81           8
        # 21       2        5            TAR      319    379      428    444    31        960       349       436     60      16           9
        # ...


    Note:
        - Images are first loaded, processed, and written to temporary files before OCR.
        - OCR results are extracted from the HOCR format output generated by Tesseract.
        - The resulting DataFrame contains information about recognized words and their positions.
        - The 'text_group' column is used to enumerate groups of related words (same line) within an image.

    """
    tesseractpath = get_short_path_name(tesseract_path)
    allimis = {}
    files2delete = []
    for ini, pi in enumerate(allpics):
        tmpfile = get_tmpfile(suffix=".png")
        loadedimg = open_image_in_cv(pi, channels_in_output=4)
        allimis[ini] = {"filename": tmpfile, "img": loadedimg}
        cv2.imwrite(tmpfile, loadedimg)

    txtout = get_tmpfile(suffix=".txt")
    txtresults = get_tmpfile(suffix=".txt")
    alltmpimagefiles = [item["filename"] for key, item in allimis.items()]
    files2delete.extend(alltmpimagefiles)
    with open(txtout, mode="w", encoding="utf-8") as f:
        f.write("\n".join(alltmpimagefiles))

    tesseractcommand = rf"""{tesseractpath} {add_after_tesseract_path} {txtout} {txtresults} hocr {add_at_the_end}"""
    tesseractcommand = re.sub(r" +", " ", tesseractcommand)
    kwargs.update(invisibledict)
    subprocess.run(tesseractcommand, **kwargs)
    with open(txtresults + ".hocr", mode="r", encoding="utf-8") as f:
        data = f.read()
    files2delete.extend([txtout, txtresults, txtresults + ".hocr"])

    df = pd.Q_Xml2df(data, add_xpath_and_snippet=False).d_unstack()
    df["group_keys"] = df.aa_all_keys.str[:-1]
    allocrresults = []
    for name, group in df.groupby("group_keys"):
        if len(group) == 4:
            if group.aa_value.iloc[0] == "ocrx_word":
                try:
                    _, page_number, word_number = group.aa_value.iloc[1].split(
                        "_", maxsplit=2
                    )
                    page_number = int(page_number)
                    word_number = int(word_number)
                    ocr_result = group.aa_value.iloc[3]
                    box, conf = group.aa_value.iloc[2].split(";", maxsplit=1)
                    conf = int(conf.split(maxsplit=1)[-1])
                    box0, box1, box2, box3 = [
                        g
                        for x in box.split()
                        if isinstance((g := try_to_convert_to_int(x)), int)
                    ]

                    allocrresults.append(
                        {
                            "id_img": page_number,
                            "id_word": word_number,
                            "ocr_result": ocr_result,
                            "start_x": box0,
                            "end_x": box2,
                            "start_y": box1,
                            "end_y": box3,
                            "conf": conf,
                            "group_keys": group.group_keys.iloc[0],
                        }
                    )
                except Exception as fe:
                    pass

    df = pd.DataFrame(allocrresults).drop_duplicates().reset_index(drop=True)
    df["start_x"] = df["start_x"].astype(np.uint32)
    df["end_x"] = df["end_x"].astype(np.uint32)
    df["start_y"] = df["start_y"].astype(np.uint32)
    df["end_y"] = df["end_y"].astype(np.uint32)
    df["conf"] = df["conf"].astype(np.uint8)
    df["id_img"] = df["id_img"].astype(np.uint32)
    df["id_word"] = df["id_word"].astype(np.uint32)
    df["ocr_result"] = df["ocr_result"].astype("string")

    df["area_size"] = (
        (df["end_x"] - df["start_x"]) * (df["end_y"] - df["start_y"])
    ).astype(np.uint32)

    df["x_center"] = ((df["start_x"] + df["end_x"]) / 2).astype(np.uint32)
    df["y_center"] = ((df["start_y"] + df["end_y"]) / 2).astype(np.uint32)

    df["width"] = (df["end_x"] - df["start_x"]).astype(np.uint32)
    df["height"] = (df["end_y"] - df["start_y"]).astype(np.uint32)
    df.group_keys = df.group_keys.str[:-1]
    df = df.ds_enumerate_groups(
        enumerated_column="text_group", column_to_enumerate="group_keys"
    )
    df = df.drop(columns=["group_keys"])
    for tmpfile in files2delete:
        try:
            os.remove(tmpfile)
        except Exception:
            continue

    return df



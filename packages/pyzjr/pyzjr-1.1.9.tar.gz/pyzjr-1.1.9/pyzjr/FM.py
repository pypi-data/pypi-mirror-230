# --------------------------------------- #
# Used for some operations on files,
# file management is abbreviated as FM.
# --------------------------------------- #
import cv2
import os
import datetime
import shutil
import tqdm
import imghdr
from os import getcwd
import win32com.client, gc

def getPhotopath(paths,cd=False,debug=True):
    """
    * log
        0.0.19以后修改了一个比较大的bug
        1.0.2后将图片和所有文件路径分开
        1.0.5功能全部完善,不会再进行更新
    :param paths: 文件夹路径
    :param cd: 添加当前运行的路径名,这是使用了相对路径才能用的
    :param debug: 开启打印文件名错误的名字
    :return: 包含图片路径的列表
    """
    img_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff', 'webp', 'raw']
    imgfile = []
    allfile = []
    file_list = os.listdir(paths)
    for i in file_list:
        if debug:
            if i[0] in ['n', 't', 'r', 'b', 'f'] or i[0].isdigit():
                print(f"[pyzjr]: File name:Error occurred at the beginning of {i}!")
        newph = os.path.join(paths, i).replace("\\", "/")
        allfile.append(newph)
        _, file_ext = os.path.splitext(newph)
        if file_ext[1:] in img_formats:
            imgfile.append(newph)
    if cd:
        cdd = getcwd()
        imgfile = [os.path.join(cdd, file).replace("\\", "/") for file in imgfile]
        allfile = [os.path.join(cdd, file).replace("\\", "/") for file in allfile]
    return imgfile, allfile


def RenameFile(image_folder_path, save_image_folder_path, newbasename='re', type=3, format=None):
    """
    对图像文件夹进行重命名
    :param image_folder_path: 输入图像的路径
    :param save_image_folder_path: 保存图像的路径
    :param newbasename: 基础名
    :param type: 默认为3——001、002、003、004...
    :param format: 扩展名,如png、jpg,默认用原本的扩展名
    :return:
    """
    savepath = CreateFolder(save_image_folder_path, debug=False)
    imglist, allist = getPhotopath(image_folder_path, debug=False)

    total_files = len(imglist)
    for i, file in tqdm.tqdm(enumerate(imglist), total=total_files, desc='Renaming files'):
        properties = os.path.basename(file)
        name, ext = os.path.splitext(properties)
        padded_i = str(i).zfill(type)
        if format is not None:
            newname = f"{newbasename}{padded_i}."+format
        else:
            newname = f"{newbasename}{padded_i}.{ext[1:]}"
        new_path = os.path.join(savepath, newname)
        shutil.copy(file, new_path)
    print("[pyzjr]:Batch renaming and saving of files completed!")


def CreateFolder(folder_path,debug=True):
    """确保文件夹存在"""
    if not os.path.exists(folder_path):
        try:
            os.mkdir(folder_path)
            if debug:
                print(f"[pyzjr]:Folder_{folder_path} created successfully!")
        except OSError:
            if debug:
                print(f"[pyzjr]:Folder_{folder_path} creation failed!")
    else:
        if debug:
            print(f"[pyzjr]:Folder_{folder_path} already exists!")
    return folder_path


def ImageAttribute(image):
    """获取图片属性"""
    properties = {}
    if isinstance(image, str):  # 如果传入的是文件路径
        properties['name'] = os.path.basename(image)
        properties['format'] = imghdr.what(image)
        properties['fsize'] = os.path.getsize(image)
        image = cv2.imread(image)
    else:  # 如果传入的是图片数据
        properties['name'] = "Nan"
        properties['format'] = "Nan"
        properties['fsize'] = image.nbytes
    properties["shape"] = image.shape
    properties["dtype"] = image.dtype
    properties['size'] = image.size
    return properties


def logdir(save_dir=r'log'):
    """
    创建训练时储存损失文件的路径
    """
    time_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y_%m_%d_%H_%M_%S')
    log_dir = os.path.join(save_dir, "loss_" + str(time_str))
    os.makedirs(log_dir,exist_ok=True)
    return log_dir


class Microsoft2PDF():
    """Convert Microsoft Office documents (Word, Excel, PowerPoint) to PDF format"""
    def __init__(self,filePath = ""):
        """
        :param filePath: If the default is a null character, it defaults to the current path
        """
        self.flagW = self.flagE = self.flagP = 1
        self.words = []
        self.ppts = []
        self.excels = []

        if filePath == "":
            filePath = getcwd()
        folder = filePath + '\\pdf\\'
        self.folder = CreateFolder(folder, debug=False)

        self.filePath = filePath
        for i in os.listdir(self.filePath):
            if i.endswith(('.doc', 'docx')):
                self.words.append(i)
            if i.endswith(('.ppt', 'pptx')):
                self.ppts.append(i)
            if i.endswith(('.xls', 'xlsx')):
                self.excels.append(i)

        if len(self.words) < 1:
            print("\n[pyzjr]:No Word files\n")
            self.flagW = 0
        if len(self.ppts) < 1:
            print("\n[pyzjr]:No PPT file\n")
            self.flagE = 0
        if len(self.excels) < 1:
            print("\n[pyzjr]:No Excel file\n")
            self.flagP = 0

    def Word2Pdf(self):
        if self.flagW == 0:
            return 0
        else:
            print("\n[Start Word -> PDF conversion]")
            try:
                print("Open Word Process...")
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = 0
                word.DisplayAlerts = False
                doc = None
                for i in range(len(self.words)):
                    print(i)
                    fileName = self.words[i]  # file name
                    fromFile = os.path.join(self.filePath, fileName)  # file address
                    toFileName = self.changeSufix2Pdf(fileName)  # Generated file name
                    toFile = self.toFileJoin(toFileName)  # Generated file address

                    print("Conversion:" + fileName + "in files...")
                    try:
                        doc = word.Documents.Open(fromFile)
                        doc.SaveAs(toFile, 17)
                        print("Convert to:" + toFileName + "file completion")
                    except Exception as e:
                        print(e)

                print("All Word files have been printed")
                print("End Word Process...\n")
                doc.Close()
                doc = None
                word.Quit()
                word = None
            except Exception as e:
                print(e)
            finally:
                gc.collect()

    def Excel2Pdf(self):
        if self.flagE == 0:
            return 0
        else:
            print("\n[Start Excel -> PDF conversion]")
            try:
                print("open Excel Process...")
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = 0
                excel.DisplayAlerts = False
                wb = None
                ws = None
                for i in range(len(self.excels)):
                    print(i)
                    fileName = self.excels[i]
                    fromFile = os.path.join(self.filePath, fileName)

                    print("Conversion:" + fileName + "in files...")
                    try:
                        wb = excel.Workbooks.Open(fromFile)
                        for j in range(wb.Worksheets.Count):  # Number of worksheets, one workbook may have multiple worksheets
                            toFileName = self.addWorksheetsOrder(fileName, j + 1)
                            toFile = self.toFileJoin(toFileName)

                            ws = wb.Worksheets(j + 1)
                            ws.ExportAsFixedFormat(0, toFile)
                            print("Convert to:" + toFileName + "file completion")
                    except Exception as e:
                        print(e)
                print("All Excel files have been printed")
                print("Ending Excel process...\n")
                ws = None
                wb.Close()
                wb = None
                excel.Quit()
                excel = None
            except Exception as e:
                print(e)
            finally:
                gc.collect()

    def PPt2Pdf(self):
        if self.flagP == 0:
            return 0
        else:
            print("\n[Start PPT -> PDF conversion]")
            try:
                print("Open PowerPoint process...")
                powerpoint = win32com.client.Dispatch("PowerPoint.Application")
                ppt = None
                for i in range(len(self.ppts)):
                    print(i)
                    fileName = self.ppts[i]
                    fromFile = os.path.join(self.filePath, fileName)
                    toFileName = self.changeSufix2Pdf(fileName)
                    toFile = self.toFileJoin(toFileName)

                    print("Conversion:" + fileName + "in files...")
                    try:
                        ppt = powerpoint.Presentations.Open(fromFile, WithWindow=False)
                        if ppt.Slides.Count > 0:
                            ppt.SaveAs(toFile, 32)
                            print("Convert to:" + toFileName + "file completion")
                        else:
                            print("Error, unexpected: This file is empty, skipping this file")
                    except Exception as e:
                        print(e)
                print("All PPT files have been printed")
                print("Ending PowerPoint process...\n")
                ppt.Close()
                ppt = None
                powerpoint.Quit()
                powerpoint = None
            except Exception as e:
                print(e)
            finally:
                gc.collect()

    def WEP2Pdf(self):
        """
        Word, Excel and PPt are all converted to PDF.
        If there are many files, it may take some time
        """
        print("Convert Microsoft Three Musketeers to PDF")
        self.Word2Pdf()
        self.Excel2Pdf()
        self.PPt2Pdf()
        print(f"All files have been converted, you can find them in the {self.folder}")

    def changeSufix2Pdf(self,file):
        """Change the file suffix to .pdf"""
        return file[:file.rfind('.')] + ".pdf"

    def addWorksheetsOrder(self,file, i):
        """Add worksheet order to file name"""
        return file[:file.rfind('.')] + "_worksheet" + str(i) + ".pdf"

    def toFileJoin(self, file):
        """Connect the file path and file name to the complete file path"""
        return os.path.join(self.filePath, 'pdf', file[:file.rfind('.')] + ".pdf")
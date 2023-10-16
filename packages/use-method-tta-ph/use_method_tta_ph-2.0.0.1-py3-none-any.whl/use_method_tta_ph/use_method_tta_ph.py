import struct
import binascii
import shutil
import boto3.session
from PIL import Image, ImageDraw, ImageFont, ExifTags
import os
import re
import regex
import random
from alive_progress import alive_bar
from shapely.geometry import Polygon
from shapely.geometry import box
from smart_open import open as op
from dataclasses import dataclass
import requests
import logging
import datetime
from google.cloud import storage

# end_point_url_2022 = "https://kr.object.ncloudstorage.com"
end_point_url_2023 = "https://kr.object.gov-ncloudstorage.com"
origin_data_path = "../data/origin/"
label_data_path = "../data/label/"
download_bucket_name = "cw_platform"
upload_bucket_name = "ttl_cw_project_operation"

storage_client = storage.Client()
source_bucket = storage_client.bucket(download_bucket_name)
upload_bucket = storage_client.bucket(upload_bucket_name)

current_directory_path = os.path.dirname(os.path.abspath(__file__))
pattern = r'(\d+-\d+)'
# 필수
####

"""
    TTA 데이터 품질 검증 프로젝트에서 데이터 전처리 하면서 필요한 모듈들을 정리
    S3 버킷에 접속, 버킷내 파일 확인, 필요한 샘플링 작업 진행!!
    압축 파일 생성, 시각화 이미지, box, polygon IoU 값 계산 등
    필요한 메소드들을 차근히 정리해서 만들어 놓자
"""

# dataclasses 모듈을 사용
# 특정한 매직 메서드를 자동으로 만들어줌
# 변수 어노테이션이 붙어 있는 어트리뷰트(클래스 내의 변수나 메서드)를 찾음
# 자세한 내용은 검색으로 확인 ex> https://velog.io/@sawol/데이터-클래스dataclasses


@dataclass
class Return_values:
    x1: float
    y1: float
    x2: float
    y2: float


"""
    log파일로 error 나 이슈되는 사항을 저장
"""
def makeLog():
    match = re.search(pattern, current_directory_path)
    logger = logging.getLogger(match.group(1))
    lgo_level = logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # add the handler to the logger
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(log_format)
    logger.setLevel(lgo_level)
    logger.addHandler(stream_hander)
    # set up lagging to file
    os.makedirs(os.path.join(current_directory_path, "log"), exist_ok=True)
    log_filename = f"{os.path.join(current_directory_path, 'log')}/{datetime.datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename)
    logger.addHandler(file_handler)

    return logger

"""
    데이터 처리(다운로드, preset, obj 수량 등등)을 완료 햇을때
    슬렉 메세지로 전달해 준다
"""
def send_message(message):
    # 생성한 웹훅 주소
    hook = "https://hooks.slack.com/services/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"
    title = "작업 완료, 결과를 확인해주세요."
    content = message

    # 메시지 전송
    requests.post(
        hook,
        headers={"content-type": "application/json"},
        json={
            "text": title,
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"{content}건의 결과가 처리되었습니다."},
                }
            ],
        },
    )
def download_blob(source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # download_bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    blob = source_bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")
    
def upload_blob(source_file_name, destination_blob_name, user_email_lis=[]):
    """Uploads a file to the bucket."""
    # upload_bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    blob = upload_bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # 2023년 1월~2월 버킷 정책 변경으로 해당 내용 주석 처리
    # - 기존: pm_downloads/ 버킷 업로드 -> 객체 ACL 수정해 직접 다운로드
    # - 변경: 4개의 프로젝트 운영 버킷 중 ttl_cw_project_operation/ 버킷 업로드 -> 다운로드 센터 URL 전달
    # acl = blob.acl
    # for user_email in user_email_list:
    #     acl.user(user_email).grant_read()
    # acl.save()

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def upload_and_make_downlaod_link(upload_prefix, zipfile_path):
    global upload_bucket_name
    # 1 GB 이상되는 압축파일이 있을 시 gsutil을 활용해서 압축파일 업로드 하기
    # 모듈로는 multiprocessing으로 압축파일이 업로드 되지 않기 떄문에 multiprocessing을 지원하는
    # gsutil을 활용하는게 좋을 것으로 판단
    cmd_str = ["gcloud auth login", f"gsutil -m cp -r {os.path.dirname(zipfile_path)}/'{os.path.basename(zipfile_path)}' gs://{upload_bucket_name}/{upload_prefix}'{os.path.basename(zipfile_path)}.zip'",]

    split_byte = 1073741824  # 1 GB를 Byte로 표현
    if os.path.getsize(zipfile_path) < split_byte:
        upload_blob(zipfile_path, os.path.join(upload_bucket_name, os.path.basename(zipfile_path)))
    else:
        for cmd in cmd_str:
            file_upload_result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    convert_html_file_name = file_name.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    download_link = f"https://cw-data-extract-download-dot-crowdworks-platform.appspot.com/convert_download?bucket=ttl_cw_project_operation&file_path={upload_prefix}{convert_html_file_name}"

    return download_link

class S3_controll:
    def __init__(self) -> None:
        global end_point_url_2023

        # bucket_name 변수
        self.__bucket = str()
        # target_path 즉, 버킷 내의 경로 변수
        self.__prefix = str()
        self.__aws_access_key_id = str()
        self.__aws_secret_access_key = str()
        self.__endpoint_url = end_point_url_2023
        self.__profile_name = str()
        self.__region_name = str()
        self.__s3_client = boto3.session
        self.__data_path_list = list()
        self.__s3_resource = str()

    # ---------------------------------------------------
    # Check of S3 configure setting Value
    # ---------------------------------------------------

    def _s3_connect_test(self):
        """
        s3 접속에 잘 되었는지 확인하는 함수
        """
        try:
            obj_list = self.__s3_resource.list_objects(
                Bucket=self.__bucket, Prefix=self.__prefix
            )
            try:
                contents_list = obj_list["Contents"]
                if contents_list is not Exception:
                    print("AWS Connect Success, Thank you.")
            except Exception as contents_e:
                print("Not Found Contents - Plz Check your Prefix\n", self.__prefix)

        except Exception as e:
            print("AWS Connect ERROR - View Context = ", e)

    # ---------------------------------------------------
    # AWS S3 configure setting
    # ---------------------------------------------------

    def s3_configure(
        self,
        bucket=None,
        prefix=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        # endpoint_url='https://kr.object.ncloudstorage.com',
        profile_name=None,
        region_name=None,
    ):
        send_your_except = "{} is required to connect to AWS S3."

        # ------------------------------------------------------
        # Bucket Name 저장
        # ------------------------------------------------------
        if bucket is not None:
            self.__bucket = bucket
        else:
            print(send_your_except.format("BUCKET NAME"))
            return
        # ------------------------------------------------------
        # Prefix 경로 저장
        # ------------------------------------------------------
        if prefix is not None:
            self.__prefix = prefix
        else:
            print(send_your_except.format("PREFIX"))
            return
        # ------------------------------------------------------
        # __profile_name 저장
        # 만약 __profile_name 존재할 경우 --> aws_access_key_id, aws_secret_access_key 필요 X
        # 없으면 aws_access_key_id랑 key 값을 입력해야 한다.
        # ------------------------------------------------------
        if profile_name is not None:
            self.__profile_name = profile_name
            s3_client = self.__s3_client.Session(profile_name=self.__profile_name)
            if self.__endpoint_url is not None:
                self.__s3_resource = s3_client.client(
                    service_name="s3", endpoint_url=self.__endpoint_url
                )
            else:
                self.__s3_resource = s3_client.client(service_name="s3")
        else:
            if (
                aws_access_key_id is None
                or aws_secret_access_key is None
                or region_name is None
            ):
                print(
                    send_your_except.format(
                        "'aws_access_key_id' & 'aws_secret_access_key' & '__region_name'"
                    )
                )
                return
            else:
                self.__aws_access_key_id = aws_access_key_id
                self.__aws_secret_access_key = aws_secret_access_key
                self.__region_name = region_name
                s3_client = self.__s3_client.Session(
                    aws_access_key_id=self.__aws_access_key_id,
                    aws_secret_access_key=self.__aws_secret_access_key,
                    region_name=self.__region_name,
                )
                if self.__endpoint_url is not None:
                    self.__s3_resource = s3_client.client(
                        service_name="s3", endpoint_url=self.__endpoint_url
                    )
                else:
                    self.__s3_resource = s3_client.client(service_name="s3")

        self._s3_connect_test()

        # ------------------------------------------
        # botocore.client.S3 값을 리턴!!
        # ------------------------------------------
        return self.__s3_resource

    def s3_get_path_list(self):
        if self.__bucket == "" or self.__prefix == "":
            print("To use s3_get_sample(), s3_configure() must be set.")
        else:
            with alive_bar(0, title="파일 확인: ", force_tty=True) as bar:
                pages = self.__s3_resource.get_paginator("list_objects_v2").paginate(
                    Bucket=self.__bucket, Prefix=self.__prefix
                )
                for page in pages:
                    for content in page["Contents"]:
                        obj_name = content["Key"]
                        obj_size = content["Size"]

                        if obj_size == 0:
                            continue
                        self.__data_path_list.append(obj_name)
                        bar.text = os.path.basename(obj_name)
                        bar()

        return self.__data_path_list


class S3_wavfile_check:
    """
    TypeError: no default __reduce__ due to non-trivial __cinit__
        --> pickle 문제가 있는데 이부분은 좀더 공부해야 되지만 현재는 멀티프레싱 하기에는 다소 문제점이 있음
        --> multiprocessing시 각각의 CPU가 접속하기 위해 계속적인 리셋이 필요하기에 새로이 클래스 선정
    """

    def __init__(self, bucket_name, profile_name) -> None:
        global end_point_url_2023

        self.__bucket = bucket_name
        self.__s3_client = boto3.session
        self.__profile_name = profile_name
        self.__s3_resource = str()
        self.__endpoint_url = end_point_url_2023

    def s3_wavfile_playtime_check(self, wav_path):
        blocks_2 = [
            ["Subchunk1ID", "B", 4],
            ["Subchunk1", "L", 4],
            ["AudioFormat", "L", 2],
            ["NumChannels", "L", 2],
            ["SampleRate", "L", 4],
            ["ByteRate", "L", 4],
            ["BlockAlign", "L", 2],
            ["BitsPerSample", "L", 2],
        ]
        i = 0
        extra = 0
        # sampleRate = ""
        # audioFormat = ""
        # numChannels = ""
        # bitsPerSample = ""
        play_time = 0
        data_length = 0
        tmp_arr = []  # self로 변수 설정하였더니 중복되는 값이 발생한 거 같음 그래서 함수 시작할 때마다 리셋이 필요한거 같음!!

        s3_client = self.__s3_client.Session(profile_name=self.__profile_name)
        self.__s3_resource = s3_client.client(
            service_name="s3", endpoint_url=self.__endpoint_url
        )

        def Little(data):
            if len(data) == 4:
                data = struct.pack("<I", int(binascii.b2a_hex(data), 16))
                return binascii.b2a_hex(data)
            elif len(data) == 2:
                data = struct.pack("<h", int(binascii.b2a_hex(data), 16))
                return binascii.b2a_hex(data)

        def Big(data):
            return binascii.b2a_hex(data)

        def check_s3_bucket_file_size(path):
            response = self.__s3_resource.get_object(Bucket=self.__bucket, Key=path)
            content_lenght = response["ContentLength"]

            return content_lenght

        def output_duration(length):
            hours = length // 3600
            length %= 3600
            mins = length // 60
            length %= 60
            seconds = length

            return hours, mins, seconds

        with op(
            f"s3://{self.__bucket}/{wav_path}",
            "rb",
            transport_params={"client": self.__s3_resource},
        ) as wf:
            end_flag = True
            wav_binary_data = wf.readline()
            while end_flag:
                wav_binary_data_2 = wf.readline()
                if b"data" in wav_binary_data:
                    wav_binary_data += wav_binary_data_2
                    end_flag = False
                else:
                    wav_binary_data += wav_binary_data_2

            try:
                i = (
                    str(binascii.b2a_hex(wav_binary_data))[2:].index(
                        str(binascii.hexlify(b"fmt "))[2:-1]
                    )
                    // 2
                )

            except:
                # mylogger = makeLog()
                mylogger.info(f"file_path: {wav_path}, binary_data: {wav_binary_data}")
                pass
            for blc in blocks_2:
                # if blc[1] == "B":
                #     print(f"{blc[0]} = {Big(wav_binary_data[i:i+blc[2]])} ({wav_binary_data[i:i+blc[2]]})")
                # if blc[0] == "AudioFormat":

                #     audioFormat = int(Little(wav_binary_data[i:i+blc[2]]), 16)
                if blc[0] == "NumChannels":
                    numChannels = int(Little(wav_binary_data[i : i + blc[2]]), 16)
                elif blc[0] == "SampleRate":
                    sampleRate = int(Little(wav_binary_data[i : i + blc[2]]), 16)
                elif blc[0] == "BitsPerSample":
                    bitsPerSample = int(Little(wav_binary_data[i : i + blc[2]]), 16)
                # else:
                #     print(f"{blc[0]} = {Little(wav_binary_data[i:i+blc[2]])} ({wav_binary_data[i:i+blc[2]]})")
                i += blc[2]

            # extra = str(binascii.b2a_hex(wav_binary_data))[2:].index(str(binascii.hexlify(b'data'))[2:-1]) //2 - i
            # extra_blocks = [["ExtraParmSize", "L", 2], ["ExtraParams", "L", extra - 2]]
            # if extra > 0:
            #     for blc in extra_blocks:
            #         if blc[1] == "B":
            #             print(f"{blc[0]} = {Big(wav_binary_data[i:i+blc[2]])} ({wav_binary_data[i:i+blc[2]]})")
            #         else:
            #             print(f"{blc[0]} = {Little(wav_binary_data[i:i+blc[2]])} ({wav_binary_data[i:i+blc[2]]})")
            #         i += blc[2]
            file_size = check_s3_bucket_file_size(wav_path)
            if numChannels == 1 and bitsPerSample == 8:
                data_length = file_size - 44
                play_time = data_length / sampleRate
            elif numChannels == 1 and bitsPerSample == 16:
                data_length = file_size / 2 - 22
                play_time = data_length / sampleRate
            elif numChannels == 1 and bitsPerSample == 24:
                data_length = file_size / 3 - (44 / 3)
                play_time = data_length / sampleRate
            elif numChannels == 2 and bitsPerSample == 8:
                data_length = file_size / 2 - 22
                play_time = data_length / sampleRate
            elif numChannels == 2 and bitsPerSample == 16:
                data_length = file_size / 4 - 11
                play_time = data_length / sampleRate
            else:
                data_length = file_size / 6 - (44 / 6)
                play_time = data_length / sampleRate
            hours, mins, seconds = output_duration(play_time)
            tmp_arr.append(
                {
                    "file_path": wav_path,
                    "total_play_time": f"{hours}시간 {mins}분 {round(seconds, 2)}초",
                    "origin_seconds": play_time,
                    "fs": sampleRate,
                    "len_data": data_length,
                }
            )
        return tmp_arr


class S3_download:
    def __init__(self, profile_name, bucket_name) -> None:
        global label_data_path, origin_data_path, end_point_url_2023

        self.__profile_name = profile_name
        self.__bucket_name = bucket_name
        self.__endpoint_url = end_point_url_2023
        # json 파일 다운로드 위치
        self.__label_data_path = label_data_path
        # 원천 데이터 파일 다운로드 위치
        self.__origin_data_path = origin_data_path
        self.__s3_client = boto3.session
        self.__s3_resource = str()

    def s3_bucket_file_download(self, path):
        session = self.__s3_client.Session(profile_name=self.__profile_name)
        self.__s3_resource = session.client(
            service_name="s3", endpoint_url=self.__endpoint_url
        )

        if path.endswith(".json"):
            os.makedirs(
                f"{self.__label_data_path}{os.path.dirname(path)}", exist_ok=True
            )
            file_path = os.path.join(self.__label_data_path, path)
        else:
            os.makedirs(
                f"{self.__origin_data_path}{os.path.dirname(path)}", exist_ok=True
            )
            file_path = os.path.join(self.__origin_data_path, path)

        self.__s3_resource.download_file(self.__bucket_name, path, file_path)

        return path


class Ph_use_method:
    def __init__(self) -> None:
        # 압축하려는 원천데이터 경로
        self.__source = str()
        # 압축하고자 하는 원천데이터 폴더 경로
        self.__destination = str()
        # 구분자 .(dot) 개수를 파악해서 기입
        self.__num = int()
        # 해당 폴더내에 있는 파일 수량 확인
        self.__folder_path = str()
        # 시각화 이미지를 하기위한 좌표 리스트(안에는 딕셔너리 형태로 {"file_path": file_path, "bbox": bbox_list, "polygon": polygon_list, "type": annotation_type})표현 필수
        # 이미지 오픈할 경로
        self.__img_path = str()
        # 시각화할 좌표값
        self.__data = list()
        # 리스트 내에 데이터를 랜덤으로 추출할 때 필요한 원천 리스트
        self.__folder_list = list()
        # IOU 값 계산할 때 필요한 좌표값
        self.__pred_bbox = list()
        self.__gt_bbox = list()
        self.__pred_polygon = list()
        self.__gt_polygon = list()

    def make_archive(self, source=None, destination=None, num=1) -> None:
        self.__source = source
        self.__destination = destination
        self.__num = num
        base = os.path.basename(self.__destination)
        # 폴더명에 '.' 가 있을 경우 그 숫자를 판단해야 한다. 다르게 하는 방법 모색
        name = base.split(".")[self.__num]
        format = base.split(".")[self.__num + 1]
        archive_from = os.path.dirname(self.__source)
        archive_to = os.path.basename(self.__source.strip(os.sep))
        print(archive_from)
        print(archive_to)
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move(f"{name}.{format}", self.__destination)

    def get_files_count(self, folder_path=None):
        self.__folder_path = folder_path
        dirListing = os.listdir(self.__folder_path)

        return dirListing

    def image_draw(
        self, data, path=origin_data_path, project=None, num=0, color="blue"
    ):
        """
        Ver.1 :
            Polygon, keypoint, polyline 구조는 [[x1, y1], [x2, y2] ... [Xx, Yy]] 이런식으로 이중 배열 구조로 되어 있어야 함
            bbox 구조는 [[x1, y1, x2, y2], [x1, y1, x2, y2], ...]
            함수에 사용되는 인자 구조는 [{"file_path": file_path, "bbox or polygons or keypoints or polyline": bbox or polygon or keypoints or polyline,
            "type": "bbox","polygon","etc."}]
            이러한 형태로 와야 함
        Ver.2 :
            이미지에 박스 및 폴리곤 등 2가지 형태를 그리기 위해서 함수에 사용되는 인자 구조룰 변경함
            [{"file_path": file_path, "draw_point": [{"bbox": bbox_list, "type": "bbox"}, ... {"polygon": polygon_list, "type": "polygon"},... {"keypoint": keypoint_list, "type": "keypoint"}...]}]
            구조에 맞게 아래 함수에 변경 사항 적용
            project를 설정하여 로그 파일에 프로젝트 명을 기입
        """

        def loadfont(fontsize=20):
            # ttf파일의 경로를 지정합니다.
            ttf = "/Users/parkhwan/Downloads/D2Coding-Ver1.3.2-20180524/D2CodingLigature/D2CodingBold-Ver1.3.2-20180524-ligature.ttf"
            return ImageFont.truetype(
                font=ttf,
                size=fontsize,
            )

        self.__img_path = data["file_path"]
        os.makedirs(
            f"../output/masking/{os.path.dirname(self.__img_path)}", exist_ok=True
        )
        img = Image.open(f"{path}{self.__img_path}").convert("RGB")
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            exif = dict(img.getexif().items())

            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # logging모듈로 로그 남길수 있게 다음 업데이트 준비
            mylogger.info(f"{self.__img_path}: EXIF 데이터가 없습니다.")
            pass

        if isinstance(data["draw_point"], list):  # Ver.2 에 해당하는 구조에 맞게 함수 조건 문 변경
            # draw_point 키 값에 해당하는 value의 type은 리스트 형태
            for idx, point in enumerate(data["draw_point"]):
                self.__font = loadfont()
                self.__type = point["type"]
                if point.get("text"):
                    self.__text = point["text"]  # 이미지에 박스나 폴리곤 그릴때 텍스트 추가시 필요
                if self.__type == "bbox":
                    self.__data = point["bbox"]
                elif self.__type == "polygon":
                    self.__data = point["polygon"]
                elif self.__type == "keypoints":
                    self.__data = point["keypoints"]
                else:
                    self.__data = point["polyline"]
                draw = ImageDraw.Draw(img)
                if self.__type == "polygon":
                    try:
                        tuple_poly = tuple(tuple(x) for x in self.__data)
                        if self.__text:
                            draw.line(tuple_poly + tuple_poly[0], fill=color, width=3)
                            text_pos = (tuple_poly[0][0] + 10, tuple_poly[0][1] + 10)
                            draw.text(
                                xy=text_pos,
                                text=self.__text,
                                fill=(0, 0, 255),
                                font=self.__font,
                            )
                        else:
                            draw.line(tuple_poly + tuple_poly[0], fill=color, width=3)
                            text_pos = (tuple_poly[0][0] + 10, tuple_poly[0][1] - 50)
                            draw.text(
                                xy=text_pos,
                                text=self.__text,
                                fill=(0, 0, 255),
                                font=self.__font,
                            )
                    except:
                        # print 함수로 로그하는 방법을 logging모듈을 활용할 것 다음 업데이트!!
                        # mylogger = makeLog(project)
                        mylogger.info(
                            f"이미지에 그림 그려질 Polygon 좌표가 없는 경우의 파일 경로: {self.__img_path}"
                        )
                elif self.__type == "bbox":
                    try:
                        if self.__text:
                            draw.rectangle(self.__data, outline=(255, 0, 0), width=3)
                            text_pos = (self.__data[0] + 10, self.__data[1] + 10)
                            draw.text(
                                xy=text_pos,
                                text=self.__text,
                                fill=(255, 0, 0),
                                font=self.__font,
                            )
                        else:
                            draw.rectangle(self.__data, outline=(255, 0, 0), width=3)
                            text_pos = (self.__data[0] + 10, self.__data[1] - 50)
                            draw.text(
                                xy=text_pos,
                                text=self.__text,
                                fill=(255, 0, 0),
                                font=self.__font,
                            )
                    except:
                        # print 함수로 로그하는 방법을 logging모듈을 활용할 것 다음 업데이트!!
                        mylogger.info(
                            f"이미지에 그림 그려질 Polygon 좌표가 없는 경우의 파일 경로: {self.__img_path}"
                        )
                else:
                    try:
                        tuple_poly = tuple(tuple(x) for x in self.__data)
                        draw.line(tuple_poly, fill="red", width=3)
                    except:
                        # print 함수로 로그하는 방법을 logging모듈을 활용할 것 다음 업데이트!!
                        mylogger.info(
                            f"이미지에 그림 그려질 point 좌표가 없는 경우의 파일 경로: {self.__img_path}"
                        )
        img.save(f"../output/masking/{self.__img_path}")

    def get_random(self, folder_list, cnt):
        self.__folder_list = folder_list
        tmp_list = self.__folder_list
        random.shuffle(tmp_list)

        return tmp_list[:cnt]

    def get_bbox_IoU(self, pred_bbox, gt_bbox, decimal_point=2):
        """
        bbox iou 값 계산 공식
        Input:
            bbox 구조 ex>
            pred_bbox = [{"left": 10, "top": 20, "width": 12, "height": 20}]
            gt_bbox = [{"left": 10, "top": 20, "width": 12, "height": 20}]
        Output:
            원하는 소수점 자리는 decimal_point 값을 입력하면 된다. 기본은 소수점 둘째짜리 까지!!!
            iou = 두개의 bbox 영역을 계산하여 산출해낸 iou 값
        """
        self.__pred_bbox = pred_bbox
        self.__gt_bbox = gt_bbox

        def make_bbox(bboxs):
            # (x1,y1,x2,y2) 튜플 형태로 만든다
            for bbox in bboxs:
                x1 = bbox["left"]
                y1 = bbox["top"]
                x2 = bbox["width"] + x1
                y2 = bbox["height"] + y1

                bbox_tuple = Return_values(x1, y1, x2, y2)

            return bbox_tuple

        pred_bbox_point = make_bbox(self.__pred_bbox)
        gt_bbox_point = make_bbox(self.__gt_bbox)
        pred_poly = box(
            pred_bbox_point.x1,
            pred_bbox_point.y1,
            pred_bbox_point.x2,
            pred_bbox_point.y2,
        )
        gt_poly = box(
            gt_bbox_point.x1, gt_bbox_point.y1, gt_bbox_point.x2, gt_bbox_point.y2
        )

        iou = round(
            pred_poly.intersection(gt_poly).area / pred_poly.union(gt_poly).area,
            decimal_point,
        )

        return iou

    def get_polygon_IoU(self, pred_polygon, gt_polygon, num=2):
        """
        Input:
            polygon 구조 ex>
            pred_polygon = [{"x": 1, "y": 2}, {"x": 5, "y": 10} ....]
            gt_polygon = [{"x": 1, "y": 2}, {"x": 5, "y": 10} ....]
        Output:
            iou = 2개의 polygon 좌표 영역을 계산하여 산출해낸 iou 값
        """

        self.__pred_polygon = pred_polygon
        self.__gt_polygon = gt_polygon
        # buffer(0)으로 지정하여 TopologyException: Input geom 0 is invalid 발생 문제 해결
        pred_polygon_shape = Polygon(
            [(p["x"], p["y"]) for p in self.__pred_polygon]
        ).buffer(0)
        gt_polygon_shape = Polygon(
            [(p["x"], p["y"]) for p in self.__gt_polygon]
        ).buffer(0)
        # intersection (겹치는 영역)
        intersection_area = pred_polygon_shape.intersection(gt_polygon_shape).area
        # union area (합집합 형태의) 전체 영역
        union_area = pred_polygon_shape.union(gt_polygon_shape).area

        # iou 값 단순히 계산
        iou = round(intersection_area / union_area, num)

        return iou, pred_polygon_shape, gt_polygon_shape


mylogger = makeLog()
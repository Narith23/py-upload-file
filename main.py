from datetime import datetime
import os
from typing import Union
import uuid

from fastapi import FastAPI, HTTPException, Path, status, File, UploadFile
from fastapi.responses import FileResponse

from config.config import IMAGE_PATH_FILE, IMAGE_SIZE, VIDEOS_PATH_FILE, VIDEOS_SIZE

app = FastAPI()


@app.get("/", tags=["DEFAULT"])
def read_root():
    return HTTPException(status_code=status.HTTP_200_OK, detail="APP RUNNING!")


@app.post("/upload/file/image", tags=["UPLOAD FILE IMAGE"])
def upload_file_image(image: UploadFile = File(...)):
    # Validate image file size
    if image.size > IMAGE_SIZE * 1024 * 1024:  # 1 MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="IMAGE SIZE EXCEEDS LIMIT",
        )

    extension = image.filename.rsplit(".", 1)[-1]
    # new name file
    new_name_file = (
        str(round(datetime.now().timestamp()))
        + "_"
        + str(datetime.now().microsecond)
        + "_"
        + uuid.uuid4().hex[:6].upper()
        + "."
        + extension
    )

    try:
        file_path = f"{IMAGE_PATH_FILE}/{new_name_file}"
        # Save the file to a specific location
        with open(file_path, "wb") as f:
            content = image.file.read()
            f.write(content)
            file_size = len(content)

        values = {
            "file_name": image.filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_ext": extension,
        }

        return HTTPException(
            status_code=status.HTTP_200_OK,
            detail={"message": "FILE UPLOADED SUCCESSFULLY!", "values": values},
        )
    except HTTPException as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ERROR: " + str(e)
        )


@app.get("/show/file/image", tags=["UPLOAD FILE IMAGE"])
def show_file_image(file_path: str):
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/jpeg")
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="FILE NOT FOUND!"
        )


@app.post("/upload-video", tags=["UPLOAD VIDEO"])
async def upload_video(video: UploadFile = File(...)):
    # Validate video file size
    max_video_size = VIDEOS_SIZE * 1024 * 1024  # 10 MB limit
    if video.size > max_video_size:
        raise HTTPException(status_code=413, detail="VIDEO SIZE EXCEEDS LIMIT")

    # Validate content type (optional)
    allowed_content_types = {"video/mp4", "video/webm"}
    if video.content_type not in allowed_content_types:
        raise HTTPException(status_code=415, detail="INVALID VIDEO FORMAT")

    # Save the video file
    try:
        extension = video.filename.rsplit(".", 1)[-1]
        # new name file
        new_name_file = (
            str(round(datetime.now().timestamp()))
            + "_"
            + str(datetime.now().microsecond)
            + "_"
            + uuid.uuid4().hex[:6].upper()
            + "."
            + extension
        )
        file_path = f"{VIDEOS_PATH_FILE}/{new_name_file}"
        with open(file_path, "wb") as f:
            content = video.file.read()
            f.write(content)
            file_size = len(content)

        values = {
            "file_name": video.filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_ext": extension,
        }

        return HTTPException(
            status_code=status.HTTP_200_OK,
            detail={"message": "FILE UPLOADED SUCCESSFULLY!", "values": values},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="ERROR: " + str(e))
    
    
@app.get("/videos/{video_path}", tags=["UPLOAD VIDEO"])
async def get_video(video_path: str = Path(...)):
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="VIDEO NOT FOUND")

    response = FileResponse(video_path, media_type="video/mp4")
    return response

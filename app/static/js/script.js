document.getElementById('btn_selectImage').addEventListener('click', function() {
    document.getElementById('uploadImage').click(); // Mở hộp thoại chọn file
});

document.getElementById('uploadImage').addEventListener('change', function(event) {
    const file = event.target.files[0]; // Lấy file đầu tiên từ danh sách file được chọn
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Hiển thị ảnh đã chọn
            const imgElement = document.getElementById('img_item');
            const previewContainer = document.getElementById('imagePreview');
            imgElement.src = e.target.result; // Gán ảnh đã tải lên cho thẻ img
            imgElement.style.display = 'block'; // Hiện ảnh lên trang
            previewContainer.style.display = 'flex'; // Hiện thẻ chứa ảnh

            // Ẩn video và canvas nếu có
            document.getElementById('video').style.display = 'none';
            document.getElementById('canvasWebcam').style.display = 'none';

            // Hiển thị lại nút mở webcam và ẩn nút chụp ảnh
            document.getElementById('btn_startWebcam').style.display = 'inline-block';
            document.getElementById('btn_takePicture').style.display = 'none';
        };
        reader.readAsDataURL(file); // Đọc file dưới dạng URL
    }
});

document.getElementById('btn_startWebcam').addEventListener('click', function() {
    document.getElementById('canvasWebcam').style.display = 'none';
    const video = document.getElementById('video');
    const imgElement = document.getElementById('img_item');
    const previewContainer = document.getElementById('imagePreview');

    // Ẩn ảnh đã chọn/chụp và thẻ chứa ảnh khi mở webcam
    imgElement.style.display = 'none';
    previewContainer.style.display = 'none';

    // Đặt kích thước video là 470x300
    video.width = 470;
    video.height = 300;

    // Khởi tạo webcam
    navigator.mediaDevices.getUserMedia({ video: { width: 470, height: 300 } })
        .then(function(stream) {
            video.srcObject = stream; // Gán luồng video vào thẻ video
            video.play(); // Bắt đầu phát video
            video.style.display = 'block'; // Hiện video lên trang

            // Hiển thị nút chụp ảnh
            document.getElementById('btn_startWebcam').style.display = 'none';
            document.getElementById('btn_takePicture').style.display = 'inline-block';
        })
        .catch(function(err) {
            console.error("Lỗi khi mở webcam: " + err);
            alert("Không thể mở webcam. Vui lòng kiểm tra quyền truy cập.");
        });
});

document.getElementById('btn_takePicture').addEventListener('click', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvasWebcam');
    const context = canvas.getContext('2d');

    canvas.width = 470;
    canvas.height = 300;
    context.drawImage(video, 0, 0, 470, 300);

    const imgElement = document.getElementById('img_item');
    const previewContainer = document.getElementById('imagePreview');
    imgElement.src = canvas.toDataURL('image/png'); // Chuyển ảnh từ canvas thành URL để hiển thị
    imgElement.style.display = 'block'; // Hiện ảnh đã chụp lên
    previewContainer.style.display = 'flex'; // Hiện thẻ chứa ảnh

    const stream = video.srcObject;
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }

    // Ẩn nút chụp và hiển thị lại nút mở webcam
    document.getElementById('btn_startWebcam').style.display = 'inline-block';
    document.getElementById('btn_takePicture').style.display = 'none';
    video.style.display = 'none';
    canvas.style.display = 'none';

    document.getElementById('uploadImage').value = ''; 
});


document.getElementById("btn_extract").addEventListener("click", async function () {
    const uploadInput = document.getElementById("uploadImage");
    const canvas = document.getElementById("canvasWebcam");
    let imageData = null;
    
    // Kiểm tra xem có ảnh được tải lên không
    if (uploadInput && uploadInput.files.length > 0) {
        const file = uploadInput.files[0];
        if (!file.type.startsWith("image/")) {
            alert("File không được hỗ trợ. Vui lòng chọn ảnh có định dạng hợp lệ.");
            return;
        }
        imageData = file;
    } else if (canvas) {
        const context = canvas.getContext('2d');
        // Kiểm tra xem canvas có dữ liệu hay không
        const pixelData = context.getImageData(0, 0, 1, 1).data; 
        if (pixelData[3] !== 0) { 
            imageData = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        }
    }
    
    // Thông báo nếu không có ảnh nào được chọn
    if (!imageData) {
        alert("Vui lòng chọn hoặc chụp một ảnh để trích xuất.");
        return;
    }
    
    // Hiển thị biểu tượng loading
    document.getElementById("lbl_status").textContent = "Đang trích xuất...";
    document.getElementById("loadingOverlay").style.display = "flex";

    // Ghi lại thời điểm bắt đầu
    const startTime = new Date();

    try {
        // Lấy chỉ số ảnh từ API /img_index
        const imgIndexResponse = await fetch('/img_index');
        if (!imgIndexResponse.ok) throw new Error('Không thể lấy chỉ số ảnh.');
        const imgIndexData = await imgIndexResponse.json();
        const imgIndex = imgIndexData.unique_images_count;
        const imgName = "image_" + imgIndex + ".png";

        // Gửi ảnh tới API /predict
        const formData = new FormData();
        formData.append("file", imageData, imgName);

        const predictResponse = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });
        if (!predictResponse.ok) throw new Error('Có lỗi xảy ra khi gọi API /predict.');

        // Lấy kết quả từ API /results
        const resultsResponse = await fetch(`/results?image_name=${imgName}`);
        if (!resultsResponse.ok) throw new Error('Có lỗi xảy ra khi gọi API /results.');
        const resultsData = await resultsResponse.json();

        // Cập nhật kết quả
        document.getElementById("txt_personID").value = resultsData[0]?.personID || "";
        document.getElementById("txt_fullName").value = resultsData[0]?.name || "";
        document.getElementById("txt_birthday").value = resultsData[0]?.date_of_birth || "";
        document.getElementById("txt_gender").value = resultsData[0]?.gender || "";
        document.getElementById("txt_nation").value = resultsData[0]?.nation || "";
        document.getElementById("txt_origin").value = resultsData[0]?.hometown || "";
        document.getElementById("txt_residence").value = resultsData[0]?.permanent_residence || "";
        document.getElementById("txt_expiry").value = resultsData[0]?.date_of_expiry || "";

    } catch (error) {
        console.error('Có lỗi xảy ra:', error);
        alert(`Có lỗi xảy ra: ${error.message}`);
    } finally {
        // Ẩn biểu tượng loading
        document.getElementById("loadingOverlay").style.display = "none";

        // Ghi lại thời gian trích xuất
        const endTime = new Date();
        const timeDiff = endTime - startTime;
        const seconds = Math.floor((timeDiff / 1000) % 60);
        const minutes = Math.floor((timeDiff / 1000 / 60) % 60);
        document.getElementById("lbl_status").textContent = `Hoàn tất! Thời gian trích xuất: ${minutes} phút, ${seconds} giây.`;
    }
});


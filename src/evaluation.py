from sklearn.metrics import confusion_matrix, classification_report,accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import tensorflow as tf
import cv2
from preprocessing import preprocess_image_detect
# đánh giá mô hình dựa vào confusion matrix và classification_report
def evalute_model(model,test_dt):
    class_names = list(test_dt.class_indices.keys())
    y_true = test_dt.classes
    y_pred_probs = model.predict(test_dt)
    y_pred = np.argmax(y_pred_probs, axis=1)
    # Tạo ma trận nhầm lẫn
    cm = confusion_matrix(y_true, y_pred)
    # Vẽ ma trận nhầm lẫn
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix")
    plt.show()
    print(classification_report(y_true, y_pred, target_names=class_names))
# đánh giá mô hình bằng learning_curve
def learning_curve(history):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))  # 1 hàng, 2 cột
    # Plot training & validation accuracy
    axes[0].plot(history.history['accuracy'], label='train')
    axes[0].plot(history.history['val_accuracy'], label='val')
    axes[0].set_title('Model Accuracy')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend(loc='upper left')

    # Plot training & validation loss
    axes[1].plot(history.history['loss'], label='train')
    axes[1].plot(history.history['val_loss'], label='val')
    axes[1].set_title('Model Loss')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend(loc='upper left')

    plt.tight_layout()
    plt.show()
# hàm trả về heatmap grad_cam++
def grad_cam_plus(model, image, layer_name, class_idx=None):
    # Create gradient model
    grad_model = tf.keras.models.Model(
        inputs=[model.inputs],
        outputs=[model.get_layer(layer_name).output, model.output]
    )
    
    # Compute gradients
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image)
        if class_idx is None:
            class_idx = tf.argmax(predictions[0])
        loss = predictions[:, class_idx]
    
    grads = tape.gradient(loss, conv_outputs)
    
    # Grad-CAM++ specific calculations 
    first_deriv = grads
    second_deriv = tf.square(grads)
    third_deriv = tf.pow(grads, 3)
    
    # Global sum (hoặc mean)
    global_sum = tf.reduce_mean(conv_outputs, axis=[1, 2], keepdims=True)
    
    # Calculate alpha weights
    alpha_num = second_deriv
    alpha_denom = 2.0 * second_deriv + third_deriv * global_sum
    alpha_denom = tf.where(alpha_denom != 0.0, alpha_denom, tf.ones_like(alpha_denom))
    alphas = alpha_num / alpha_denom
    
    # Weights with ReLU
    weights = tf.reduce_sum(alphas * tf.nn.relu(grads), axis=[1, 2])
    
    # Create heatmap
    cam = tf.reduce_sum(weights[:, tf.newaxis, tf.newaxis, :] * conv_outputs, axis=-1)
    cam = tf.nn.relu(cam)
    cam = cam[0].numpy()
    
    # Normalize
    cam = cv2.resize(cam, (image.shape[2], image.shape[1]))
    cam = np.maximum(cam, 0)
    heatmap = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    
    return class_idx, heatmap
# hàm duyệt qua thư mục test cho từng thư mục 
def showGradCamPlus(mode,model,prefix):
    last_conv_layer_name = "conv5_block16_concat"
    modelIdx = 1
    if prefix =="Resnet50":
        last_conv_layer_name = "conv5_block3_out"
        modelIdx = 0
    elif prefix =="EfficientNetB0":
        last_conv_layer_name = "top_conv"
        modelIdx = 2
    class_name = { 0: "Bình thường", 1: "Vi khuẩn",2:"Virus"}
    postfix = { 0: "normal", 1: "bacter",2:"virus"}
    path, label = (
        ("chest_xray/test/NORMAL", 0) if mode == 0 else
        ("chest_xray/test/PNEUMONIA_bacteria",1) if mode == 1 else
        ("chest_xray/test/PNEUMONIA_virus", 2)
    )
    images = []
    for img_name in os.listdir(path):
        images.append((os.path.join(path, img_name), label))
    for i, (img_path, label) in enumerate(images):
        path = prefix+"/"+ postfix[label]+ str(i)+".png"
        img_array, orig_img = preprocess_image_detect(img_path,modelIdx)
        class_idx,heatmap = grad_cam_plus(model, img_array, last_conv_layer_name)
        class_idx = int(class_idx)
        heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
        superimposed_img = cv2.addWeighted(orig_img.astype(np.uint8), 0.6, heatmap_color, 0.4, 0)
        plt.figure(figsize=(10, 5))
        
        # Ảnh gốc
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB))
        plt.title(f"Ảnh gốc {i+1}\nNhãn thật: {class_name[label]}", fontsize=12)
        plt.axis('off')
        
        # Ảnh Grad-CAM++
        plt.subplot(1, 2, 2)
        plt.imshow(cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB))
        plt.title(f"Grad-CAM++{i+1}\nDự đoán: {class_name[class_idx]}", fontsize=12)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()
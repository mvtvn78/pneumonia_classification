import tensorflow as tf
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from util import generateUnique as gn
from werkzeug.utils import secure_filename
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
def make_heatmap(m,img_array,orig_img,last_conv_layer_name,class_idx,class_names):
    orig_img = np.array(orig_img)
    _,heatmap = grad_cam_plus(m, img_array, last_conv_layer_name,class_idx)
    heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    superimposed_img = cv2.addWeighted(orig_img.astype(np.uint8), 0.6, heatmap_color, 0.4, 0)
    fileName = secure_filename(f"{gn.generateUniqueTimestamp()}.png")
    path = "store\\" + fileName
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB))
    plt.title(f"Ảnh gốc", fontsize=12)
    plt.axis('off')
        
    # Ảnh Grad-CAM++
    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB))
    plt.title(f"Grad-CAM++\n Dự đoán {class_names[class_idx]}", fontsize=12)
    plt.axis('off')
        
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    return fileName
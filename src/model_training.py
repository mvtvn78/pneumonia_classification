from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping,ReduceLROnPlateau,ModelCheckpoint
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Flatten, Dense, Dropout,BatchNormalization,Activation
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from tensorflow.keras.applications.densenet import preprocess_input as densenet_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications import EfficientNetB0,DenseNet121
import os
from tensorflow.keras.regularizers import l2
from evaluation import learning_curve,evalute_model,showGradCamPlus
TRAIN_DIR = "chest_xray/train"
VAL_DIR = "chest_xray/val"
TEST_DIR ="chest_xray/test"
SEED = 42
IMG_SIZE = 224
IMG_CHANNEL = 3
BATCH_SIZE = 32
EPOCHS = 30
EARLY = 3
REDUCE = 2
# Hàm đếm số lượng lớp có trong datagen
def countClass(dt_gen):
    print("Số lớp:", dt_gen.num_classes)
    print("Danh sách lớp:", dt_gen.class_indices)
    for class_name, _ in dt_gen.class_indices.items():
        count = len([
            f for f in dt_gen.filepaths
            if os.path.basename(os.path.dirname(f)) == class_name
        ])
        print(f"{class_name}: {count} ảnh")
# Hàm tính toán trọng số class_weight cho mô hình không thiện vị (chế độ cân bằng)
def calculate_class_weights(dt_gen):
    class_weights = compute_class_weight(
        'balanced',
        classes=np.unique(dt_gen.classes),
        y=dt_gen.classes
    )
    return dict(enumerate(class_weights))
# Hàm huấn luyện mô hình 
def trainModel(model,nameFile,preprocess_input):
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        brightness_range=[0.9, 1.1],
        fill_mode='nearest',
        validation_split=0.1
        )
    train_gen = train_datagen.flow_from_directory(
            TRAIN_DIR,
            target_size=(IMG_SIZE,IMG_SIZE),
            batch_size=BATCH_SIZE,
            seed=SEED,
            subset='training',
            class_mode='categorical',
            shuffle=True
        )
    val_gen = train_datagen.flow_from_directory(
            TRAIN_DIR,
            target_size=(IMG_SIZE,IMG_SIZE),
            batch_size=BATCH_SIZE,
            seed=SEED,
            subset='validation',
            class_mode='categorical',
            shuffle=False
        )
    print("=======TRAIN=======")
    countClass(train_gen)
    print("=======VAL=======")
    countClass(val_gen)
    class_weights_dict  = calculate_class_weights(train_gen)
    print(class_weights_dict)
    with tf.device('/GPU:0'):
      path = "best_model/"+nameFile
      early_stop = EarlyStopping(
        monitor='val_loss',
        patience=EARLY,
        restore_best_weights=True
      )
      reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.1,
        patience=REDUCE,
        min_lr=1e-6,
        verbose=1
      )
      checkpoint = ModelCheckpoint(
        filepath=path,
        monitor='val_loss',
        save_best_only=True,
        save_weights_only=False,
        verbose=1
      )
      history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        class_weight=class_weights_dict,
        callbacks=[reduce_lr, checkpoint, early_stop],
        workers=4,        
      )
      return history
# Hàm Resnet50 trainning
def resnet50():
    # Sử dụng kỹ thuật transfer learning 
    resnet = ResNet50( weights='imagenet',include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, IMG_CHANNEL))
    # đóng băng các tầng trọng số
    resnet.trainable = False
    # sử dụng chính quy thêm phần head để huấn luyện mô hình
    x = layers.GlobalAveragePooling2D()(resnet.output)
    x = Dense(512,kernel_regularizer=l2(0.01), bias_regularizer=l2(0.01))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x= Dropout(0.2) (x)
    output = Dense(3, activation='softmax')(x)
    model_rn = Model(inputs=resnet.inputs, outputs=output)
    model_rn.summary()
    # sử dụng label_smoothing để mô hình học không cần quá chuẩn xác
    model_rn.compile(
        optimizer=tf.keras.optimizers.Adam(1e-4),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=['accuracy']
    )
    BATCH_SIZE = 32
    EPOCHS = 30
    EARLY = 3
    REDUCE = 2
    hisfe_resnet50 = trainModel(model_rn,"resnet50.keras",resnet_preprocess)
    learning_curve(hisfe_resnet50)
    # Fine-tunning
    for layer in resnet.layers[-20:]: 
        layer.trainable = True
    train_datagen = ImageDataGenerator(
            preprocessing_function=resnet_preprocess,
            rotation_range=10,
            width_shift_range=0.1,
            height_shift_range=0.1,
            zoom_range=0.1,
            brightness_range=[0.9, 1.1],
            fill_mode='nearest',
            )
    train_gen = train_datagen.flow_from_directory(
                TRAIN_DIR,
                target_size=(IMG_SIZE,IMG_SIZE),
                batch_size=BATCH_SIZE,
                seed=SEED,
                class_mode='categorical',
                shuffle=True
            )
    model_rn.compile(optimizer=tf.keras.optimizers.Adam(1e-5), 
                loss='categorical_crossentropy', 
                metrics=['accuracy'])
    model_rn.fit(train_gen, epochs=5)
    model_rn.save("finet_resnet50.keras")
    test_datagen = ImageDataGenerator(preprocessing_function=resnet_preprocess)
    test_gen = test_datagen.flow_from_directory(
            TEST_DIR,
            target_size=(IMG_SIZE,IMG_SIZE),
            batch_size=BATCH_SIZE,
            seed=SEED,
            class_mode='categorical',
            shuffle=False
        )
    print("=======TEST=======")
    countClass(test_gen)
    evalute_model(model_rn,test_gen)
    rn = load_model("finet_resnet50.keras")
    showGradCamPlus(0,rn,"Resnet50")
    showGradCamPlus(1,rn,"Resnet50")
    showGradCamPlus(2,rn,"Resnet50")

# Hàm EfficientNetB0 trainning
def efficientnetb0():
    effnet = EfficientNetB0(weights=None, include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, IMG_CHANNEL))
    for layer in effnet.layers:
        layer.trainable = True
    x = layers.GlobalAveragePooling2D()(effnet.output)
    x = Dense(160,kernel_regularizer=l2(1e-3))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x= Dropout(0.2)(x)
    output = Dense(3, activation='softmax')(x)
    model_effnet = Model(inputs=effnet.inputs, outputs=output)
    model_effnet.summary()
    model_effnet.compile(
    optimizer='adam',
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy']
    )
    BATCH_SIZE = 16
    EPOCHS = 50
    EARLY = 10
    REDUCE = 5
    his_effnet = trainModel(model_effnet,"EfficientNetB0.keras",efficientnet_preprocess)
    learning_curve(his_effnet)
    test_datagen = ImageDataGenerator(preprocessing_function=efficientnet_preprocess)
    test_gen = test_datagen.flow_from_directory(
                TEST_DIR,
                target_size=(IMG_SIZE,IMG_SIZE),
                batch_size=BATCH_SIZE,
                seed=SEED,
                class_mode='categorical',
                shuffle=False
            )
    evalute_model(model_effnet,test_gen)
    eff = load_model("best_model/EfficientNetB0.keras")
    showGradCamPlus(0,eff,"EfficientNetB0")
    showGradCamPlus(1,eff,"EfficientNetB0")
    showGradCamPlus(2,eff,"EfficientNetB0")
# Hàm DenseNet121 trainning
def densenet121():
    densenet = DenseNet121(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, IMG_CHANNEL))
    fine= 50
    for layer in densenet.layers[:-fine]:
        layer.trainable = False
    for layer in densenet.layers[-fine:]:
        layer.trainable = True
    x = layers.GlobalAveragePooling2D()(densenet.output)
    x = Dense(256,kernel_regularizer=l2(5e-2))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x= Dropout(0.5)(x)
    output = Dense(3, activation='softmax')(x)

    model_dense = Model(inputs=densenet.inputs, outputs=output)
    model_dense.summary()
    model_dense.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy']
    )
    BATCH_SIZE = 32
    EPOCHS = 20
    EARLY = 5
    REDUCE = 3
    his_dense = trainModel(model_dense,"DenseNet121.keras",densenet_preprocess)
    learning_curve(his_dense)
    test_datagen = ImageDataGenerator(preprocessing_function=densenet_preprocess)
    test_gen = test_datagen.flow_from_directory(
                TEST_DIR,
                target_size=(IMG_SIZE,IMG_SIZE),
                batch_size=BATCH_SIZE,
                seed=SEED,
                class_mode='categorical',
                shuffle=False
            )
    evalute_model(model_dense,test_gen)
    ds = load_model("best_model/DenseNet121.keras")
    showGradCamPlus(0,ds,"DenseNet121")
    showGradCamPlus(1,ds,"DenseNet121")
    showGradCamPlus(2,ds,"DenseNet121")
# densenet121()
# efficientnetb0()
# resnet50()
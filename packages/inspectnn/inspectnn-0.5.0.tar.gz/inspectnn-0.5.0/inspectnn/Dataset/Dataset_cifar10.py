from sklearn.model_selection import train_test_split
import numpy as np, tensorflow as tf, random

def preprocess_image_input(input_images):
    input_images = input_images.astype('float32')
    output_ims = tf.keras.applications.resnet50.preprocess_input(input_images)
    return output_ims

    
def Dataset_cifar10(num_of_samples,sequenzial=False):
    
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=1)

    # Preprocess the data
    x_train_a = x_train.astype('float32')
    x_test_a = x_test.astype('float32')
    x_val_a = x_val.astype('float32')

    x_train_a /= 255
    x_test_a /= 255
    x_val_a /= 255

    x_test = np.uint8(x_test)
    if(num_of_samples > 0):
        if sequenzial :
            dataset = range( num_of_samples)
        else:
            dataset = random.sample(range(len(x_test_a)), num_of_samples)
    else:
        dataset = [-num_of_samples]

    if(num_of_samples == 1):
        print("Dataset:",dataset)
    #print(x_test.shape)
    
    #dataset= [15]
    c10_images = [x_test_a[i] for i in dataset ]
    c10_labels = [y_test[i][0] for i in dataset]

    c10_images_apx = [x_test[i] for i in dataset ]
    c10_labels_apx = c10_labels

    return c10_images_apx,c10_labels_apx,c10_images,c10_labels


  
def Dataset_cifar10_resnet50(num_of_samples,sequenzial=False):
    
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=1)


    x_train_a = preprocess_image_input(x_train)
    x_test_a = preprocess_image_input(x_test)
    x_val_a = preprocess_image_input(x_val)

    x_test = np.uint8(x_test)
    if(num_of_samples > 0):
        if sequenzial :
            dataset = range( num_of_samples)
        else:
            dataset = random.sample(range(len(x_test_a)), num_of_samples)
    else:
        dataset = [-num_of_samples]

    if(num_of_samples == 1):
        print("Dataset:",dataset)
    #print(x_test.shape)
    
    #dataset= [15]
    c10_images = [x_test_a[i] for i in dataset ]
    c10_labels = [y_test[i][0] for i in dataset]

    c10_images_apx = [x_test[i] for i in dataset ]
    c10_labels_apx = c10_labels

    return c10_images,c10_labels_apx,c10_images,c10_labels

def load_percentage_images(v,num_of_samples=10000):
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=1)

    # Preprocess the data
    x_train_a = x_train.astype('float32')
    x_test_a = x_test.astype('float32')
    x_val_a = x_val.astype('float32')

    x_train_a /= 255
    x_test_a /= 255
    x_val_a /= 255

    x_test = x_test.astype('int8')
    dataset = range( num_of_samples)
    
    c10_images = [x_test_a[i] for i in dataset ]
    c10_labels = [y_test[i][0] for i in dataset]
    c10_images_apx = [x_test[i] for i in dataset ]

    result_images_apx=[]
    result_images = []
    result_labels = []
    
    for id,l in enumerate(c10_labels):
        if(v[l]>0):
            v[l]-=1
            result_images_apx.append(c10_images_apx[id])
            result_images.append(c10_images[id])
            result_labels.append(l)

    return result_images_apx,result_labels,c10_images,result_labels

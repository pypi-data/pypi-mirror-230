from sklearn.model_selection import train_test_split
import numpy as np, tensorflow as tf, random

def Dataset_mnist(num_of_samples,sequenzial=False):
    
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
    
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
    print(x_test.shape[1:])

    c10_images = [x_test_a[i] for i in dataset ]
    c10_labels = [y_test[i] for i in dataset]


    c10_images_apx = [x_test[i] for i in dataset ]
    c10_labels_apx = c10_labels


    return c10_images_apx,c10_labels_apx,c10_images,c10_labels
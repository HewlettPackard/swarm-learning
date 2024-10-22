import os
import logging

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.applications.vgg19 import VGG19
from swarmlearning.tf import SwarmCallback


default_max_epochs = 5
default_min_peers = 2


def main():
    dataDir = os.getenv('DATA_DIR', '/platform/swarmml/data')
    modelDir = os.getenv('MODEL_DIR', '/platform/swarmml/model')
    max_epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
    min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))

    (x_train, y_train), (x_test, y_test) = load_data(dataDir)

    save_dir = os.path.join(modelDir, 'saved_models')
    saved_model_name = 'cataract.h5'

    image_size = 224
    vgg = VGG19(weights="imagenet", include_top=False,input_shape=(image_size, image_size, 3))

    for layer in vgg.layers:
        layer.trainable = False

    model = Sequential()
    model.add(vgg)
    model.add(Flatten())
    model.add(Dense(1, activation="sigmoid"))
    print(model.summary())


    model.compile(optimizer="adam", loss="binary_crossentropy",
                  metrics=["accuracy"])

    swarmCallback = SwarmCallback(syncFrequency=128, minPeers=min_peers,useAdaptiveSync=False, adsValData=(x_test, y_test), adsValBatchSize=8)
    swarmCallback.logger.setLevel(logging.DEBUG)


    model.fit(x_train, y_train, batch_size=10, epochs=5, validation_data=(x_test, y_test), verbose=1, callbacks=[swarmCallback])  # swarmCallback

    swarmCallback.logger.info('Saving the final Swarm model ...')
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    model_path = os.path.join(save_dir, saved_model_name)
    model.save(model_path)
    swarmCallback.logger.info(f'Saved the trained model - {model_path}')

    swarmCallback.logger.info('Starting inference on the test data ...')
    loss, acc = model.evaluate(x_test, y_test)

    swarmCallback.logger.info('Test loss = %.5f' % (loss))
    swarmCallback.logger.info('Test accuracy = %.5f' % (acc))
    swarmCallback.logger.info(tensorflow.math.confusion_matrix(y_test,y_pred,num_classes=2,weights=None,dtype=tf.dtypes.int32,name=None))


if __name__ == '__main__':
    main()
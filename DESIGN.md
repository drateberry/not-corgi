# Not Corgi — Design Document

## 1. What I built

The concept of "Not Corgi" was partially inspired by an episode of the HBO series "Silicon Valley" wherein a character pitched the SeeFood app while only building a Hot Dog or Not Hot Dog image classifier. Taking this concept further, I wanted to test the capabilities of computer vision to identify two distinct breeds of corgis, the Cardigan Welsh Corgi and the Pembroke Welsh Corgi, two breeds that look similar to the casual observer, but have distinguishing visual features.

"Not Corgi" is composed of three components that work together to achieve the goal of identifying a breed of corgi or not-corgi based solely on visual characteristics. It was necessary to fully build and test each component in order (Model > API > Mobile) as each component depended on the one before it. 

The model component is a trained image classifier built using transfer learning from a pretrained backbone, MobileNetV3Large, with a three-class softmax output.

Access to the fully trained model is managed by an API built in Flask. The API's predict endpoint returns the predicted classification, a Grad-CAM heatmap, and probabilities for each class. Given the local only nature of this implementation, the API was designed without any authentication because it never leaves the LAN.

To facilitate easy use of the classifier, there is also a mobile application built in React Native and tested in Expo Go on an iPhone 15 Pro. The app makes the device's camera available to capture images, it normalizes the captured image to JPEG, POSTs to the API, and receives a JSON payload with classification, probabilities, and heatmap from the model.

---

## 2. Why this problem is hard: the tail-occlusion ceiling

The real challenge of this project is hidden behind its name. Deciding whether a photo shows a corgi at all is relatively simple. The difficulty came from my decision to give the Cardigan Welsh Corgi and the Pembroke Welsh Corgi separate classes instead of collapsing them into one.

The two breeds differ in tail, ear shape, coat color, and build. Cardigans have a long full tail, while Pembrokes are commonly docked shortly after birth or born naturally bobbed. Cardigan ears are larger and more rounded; Pembroke ears are smaller and more pointed. Brindle and blue merle coats appear only in Cardigans. Cardigans are also larger and more heavily boned. When launching this project, I expected the tail to be a mostly binary indicator of breed. This turned out to be shortsighted and exposed the accuracy ceiling.

What makes the problem hard is that the tail is usually not in the frame. Most photographs of dogs are portraits: the dog is facing the camera, or the shot is cropped at the shoulders, or the tail is behind the body, or the dog is sitting on it. When I reviewed the Stanford Dogs Dataset, the feature I had expected to carry the classification was missing from most of the images in the dataset.

Docking is banned or heavily restricted across much of Europe, and the Stanford Dogs Dataset is assembled from images scraped from the web without respect to region. A full tail therefore does not reliably mean Cardigan. So the tail is not merely absent much of the time; when it is present, it is not the easier identifier I had originally expected.

That leaves ear shape and coat color as the signals available in the typical photograph, and both are weaker than the tail. Ear shape is a difference of degree rather than kind, and it is sensitive to head angle and to whether the ears are perked or relaxed. Coat color can classify a corgi as a Cardigan when brindle or blue merle, but the colors the two breeds share do not indicate a breed. This is why the augmentation pipeline is deliberately mild on rotation and contrast, as aggressive versions of either would damage two of the key signals.

When a Pembroke and a Cardigan are photographed in a way that hides the tail, obscures the ears, and shows a coat color both breeds share, the pixels do not contain the information needed to tell them apart. No quantity of training data can train a model to analyze visual signals that don't exist. A knowledgeable human looking at the same cropped photograph is also guessing. That is what separates this from a model that is merely undertrained: the limit is in the data, not in the learner.

---

## 3. Framework choice: TensorFlow/Keras over PyTorch

My choice to use TensorFlow and Keras for my model training was influenced by two factors: I was familiar with it from a project in CS80 this summer, and my stretch goal was to create a LiteRT model to enable the mobile app to have a local model for primary use or fallback when an internet connection was unavailable.

Ultimately, I was unable to reach my stretch goal of LiteRT, but my prior experience with TensorFlow and Keras enabled me to utilize more features and recognize potential traps that could have looked like a better model while actually destroying accuracy.

---

## 4. The dataset

| Class     | train | val | test | total |
|-----------|-------|-----|------|-------|
| Cardigan  | 108   | 23  | 23   | 154   |
| Not_Corgi | 306   | 65  | 65   | 436   |
| Pembroke  | 127   | 27  | 27   | 181   |
| **total** | 541   | 115 | 115  | 771   |

I assembled the data for model training from two sources: the Stanford Dogs Dataset and Google Open Images. To create the corgi classes, I utilized all of the images for both corgi breeds from Stanford. To assemble the Not_Corgi class, I randomly pulled 2 images from each directory of non-corgi dogs, then randomly pulled images from Google's Open Images using Voxel51's FiftyOne Python library.

The composition of the Not Corgi class allowed the model to train on breadth of dog breeds rather than focusing on many images of a handful of breeds. It was also necessary to introduce non-dog images into the training data so that the model also recognized non-dogs as "not corgi."

Given the limited number (235) of Cardigan and Pembroke images compared to a more serious image classifier, I applied weighting in the training code to compensate for the Not Corgi class having almost 3 times the number of images as the Cardigan class. Without weighting, the model would have been incentivized to more frequently return a classification of Not Corgi, learning that Not Corgi occurred much more frequently than a corgi.

Given my prior experience with CS80's "traffic" problem set, I was concerned about near-identical frames inflating the training results, appearing to create a more accurate model, but really creating one that fails when presented an image that wasn't part of its training set. Using phash, I hashed all 771 images and compared every pair, finding two identical photos that were shipped under different IDs. The images were grouped to keep both in the same split bucket. This process still left the possibility that a single subject was represented in multiple photos from different angles, distances, or exposures. Detecting same-subject images would have required manually inspecting all of the images, or ranking them by embedding similarity then inspecting very similar images. Given the time constraints of this project, same-subject duplication is unmeasured rather than being ruled out.

---

## 5. Evaluation

Reporting a single accuracy number would not have been an accurate measure of this project. Specifically, I could likely have achieved a very high accuracy number for identifying "Corgi vs Not Corgi". But, in keeping with the nature of this project, I split the results into the two questions the model is really answering: is this a corgi, and if it is, which breed.

Confusion matrix, rows actual / columns predicted:

| Class         | Cardigan | Not_Corgi | Pembroke |
|---------------|----------|-----------|----------|
| **Cardigan**  | 15       | 1         | 7        |
| **Not_Corgi** | 1        | 63        | 1        |
| **Pembroke**  | 0        | 0         | 27       |

| Class     | Precision | Recall | n  |
|-----------|-----------|--------|----|
| Cardigan  | 0.938     | 0.652  | 23 |
| Not_Corgi | 0.984     | 0.969  | 65 |
| Pembroke  | 0.771     | 1.000  | 27 |

| Headline            | Value           |
|---------------------|-----------------|
| overall             | 0.913 (105/115) |
| corgi vs. not-corgi | 0.974 (112/115) |
| breed given corgi   | 0.840 (42/50)   |

The two questions produce very different answers. Corgi versus not-corgi is 0.974 (112 of 115). Breed given corgi is 0.840 (42 of 50). Nearly all of the remaining error sits in the corgi breed distinction.

The per-class numbers show that the failure is one-directional. Pembroke recall is 1.000; every Pembroke in the test set was correctly identified. Cardigan recall is 0.652, and seven of the eight Cardigan errors were called Pembroke. When the model has successfully identified a dog as a corgi, it doesn't randomly pick between Cardigan and Pembroke; rather it falls back on Pembroke as its default corgi class.

The model's propensity to pick Pembroke as its default corgi class explains the high Cardigan precision of 0.938. The model is less likely to classify a known corgi as a Cardigan; it is not predicting it better. Recall is the better measure for this class, and Cardigan has the lowest recall of the three classes.

I am reporting fractions and raw numbers because the test set is small enough that percentages imply more precision than is present. Breed given corgi is 42 of 50, making a single image worth two percentage points, and the 95% confidence interval on that figure runs roughly from 0.74 to 0.94. I am also using all actual corgis as the denominator, which counts the one Cardigan classified as Not_Corgi as a breed failure.

---

## 6. What Grad-CAM found: the model was right and the label was wrong

I included Grad-CAM to answer what the model is evaluating to reach its classification decision. Was it looking at the dog or were there environmental features it was using to determine not corgi or breed?

Reviewing Grad-CAM overlays on the misclassified photographs exposed a failure, not of the model, but of the dataset. An image that was labeled as a Pembroke was predicted as a Cardigan at 0.94 confidence by the model. The Grad-CAM overlay showed the proper focus on coat color and ears, a blue merle with rounded ears, traits that can only be markers on a Cardigan. 

This discovery validated that the model gives attention to the features that distinguish the breeds. This also exposed that the Stanford Dogs Dataset carries label noise on the distinction this project seeks to explore. I corrected the labeling of this one image, but I did not audit the remaining images for label accuracy.

The model does not hesitate on its classification errors. Three of eight incorrectly classified corgis in the final run were predicted with confidence between 0.96 and 0.99, making it so that no confidence threshold could filter these errors out.

---

## 7. Scope decisions

There were several scope changes that were made from my original plan. The accelerated pace of the summer semester was a key component in reducing the scope of the project and not achieving my originally stated stretch goal.

One change that I made was to ship the project as a local only build rather than configuring hosting to make the API publicly available. The local only decision also means that the API can be available at any time rather than relying on hosting to remain active. I was also able to skip shipping API authentication features. While reducing some work, this decision did increase the README documentation burden as it's necessary to provide more information to ensure a successful local run.

My original stretch goal was to create a LiteRT model that would be bundled in the mobile app and allow for on-device classification. This goal was also dropped because of available time as it would have not only required more work to create the LiteRT model from the trained Keras model, it would have also required rebuilding the React Native app from its Expo Go implementation. This stretch goal is what originally influenced my TensorFlow decision, which ended up not having as much weight to the scope of the project as originally expected.

---

## 8. How I utilized AI

For the completion of "Not Corgi" I used Anthropic's Claude Code within VSCode in the following ways:
- Creating the scaffolding and boilerplate of files

I used Claude Design to create mockups of the React Native app's UI, which I implemented as faithfully as possible when building the app.
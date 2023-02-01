
# How to get a Google Cloud Vision key to use with the OCR Pipeline

The [OCR Pipeline](https://tools.openpecha.org/pipelines/) uses [Google Cloud Vision](https://cloud.google.com/), part of the [Google Cloud platform](https://cloud.google.com/) to OCR images.

To use the OCR Pipeline, you need a **Google Cloud Vision key**.

To get one, you need:

- A Google account. Get one [here](https://accounts.google.com/).
- A credit card or debit card

> **Note:** If you don't have a credit card, contact openpecha@gmail.com. Our partners at [pecha.jobs](https://pecha.jobs) might be able to OCR images for you.

## On this page:

<div class="grid cards" markdown>

- [:material-arrow-right-circle-outline: __Creating a Google Cloud account__](#how-to-create-a-google-cloud-account)
- [:material-arrow-right-circle-outline: __Getting a Cloud Vision key__](#how-to-get-a-google-cloud-vision-key)
- [:material-arrow-right-circle-outline: __Help__](#need-help)

</div>

## How to create a Google Cloud account

### 1. Sign into Google

Make sure you're signed into [Google](https://accounts.google.com/).

### 2. Go to Google Cloud and get started

Visit https://cloud.google.com/ and select **Console**. 

<img width="1357" alt="Google Cloud home page" src="https://user-images.githubusercontent.com/51434640/214491257-aa0284e7-a800-4cb6-b6b9-ad14a4cab744.png">

> **Note**: The Google Cloud home page might not look exactly like this when you visit it. If you don't see **Console**, select **Get Started** or **Get started for free**. The sign-up process is very similar.

### 3. Agree to the terms of service for your country.

Select your country and check the box under **Terms of Service** to agree to it.

Then select **agree and continue**.

<img width="1357" alt="Google cloud signup" src="https://user-images.githubusercontent.com/51434640/214493131-bc2f7e0e-a45d-4f86-84b6-24fe22efca37.png">

> **Note**: If you selected **Get started** or **Get started for free** on the Google Cloud home page, you might see a screen like this instead:

<img width="1357" alt="Google cloud terms of service" src="https://user-images.githubusercontent.com/51434640/214493276-f3e0b02e-14a7-4a0a-b9b5-6e7beada5d51.png">

### 4. Activate your Google Cloud account

#### 4.1 Select **Activate** to start activating your account

<img width="1150" alt="Google cloud activate button" src="https://user-images.githubusercontent.com/51434640/214494664-57c198a2-d2a9-476e-a80f-12d68baa4c8a.png">

####  4.2 Fill in your account details

1. Select your country (if necessary).
2. Select a description of your organization or needs.
4. Check the box under **Terms of Service** to agree to it.
5. Select **Continue**.

<img width="1357" alt="Google Cloud account details" src="https://user-images.githubusercontent.com/51434640/214496379-0bc9ab1f-f70f-44ec-9220-1d2c3190691b.png">

#### 4.3 Create a new payments profile

1. Select **Create a new payments profile** or **Submit**.

<img width="1172" alt="Google Cloud new payments profile" src="https://user-images.githubusercontent.com/51434640/214496720-5a8eb5b8-edc2-43e6-8357-0f74d3ee22c9.png">

2. Select **Add payment method** to open a window where you can add a credit card or debit card.

<img width="1172" alt="Google Cloud payment method" src="https://user-images.githubusercontent.com/51434640/214498047-b0bb84d1-1f7a-41ec-a949-0d6f2c55c74b.png">

> **Note**: Depending on your country, you might also have an option to add a bank account.

3. Choose a payment type and add your address. Then select **Create**.

For _profile type_: 
- Select individual if you are using this account for yourself and using your personal payment info. 
- Select organization if you are using this account at an organization and are using its payment method.

<img width="1172" alt="Google cloud 4-3" src="https://user-images.githubusercontent.com/51434640/214498052-36bbafb1-9b4e-43e7-a9ac-29fcf06db22e.png">

4. Add your account information and select **Save card**.

<img width="1172" alt="Google cloud 4-5" src="https://user-images.githubusercontent.com/51434640/214499279-52a0730a-2fdd-4d58-a703-075155f39ac4.png">

#### 4.4 Select **Start my free trial** 

<img width="1172" alt="Google cloud Start my free trial" src="https://user-images.githubusercontent.com/51434640/214500727-694de3d1-5677-4672-af72-68aaf6a8274e.png">

Your account is now complete. Google Cloud should look now like something like this:

<img width="1244" alt="Google Cloud dashboard" src="https://user-images.githubusercontent.com/51434640/214504304-bc9c7bce-40e7-4f98-8212-9ecfd3d90874.png">

## How to get a Google Cloud Vision key

Now that you have a Google Cloud account, it's time to get a Cloud Vision key.

### 1. Open My first project

On the Google Cloud dashboard, find **My first project** and select **Go to project details**. Or go to the dropdown project menu at the top of the dashboard, find **My first project**, and open it.

<img width="1244" alt="My first project" src="https://user-images.githubusercontent.com/51434640/214504058-49e8b831-90bb-4716-b41a-39243b4ece3d.png">

### 2. Add Google Cloud Vision to your project

1. With **My first project** open, enter **Cloud Vision** in Google Cloud console's search bar and choose **Cloud Vision API**. 

<img width="1420" alt="Searching for cloud vision (1)" src="https://user-images.githubusercontent.com/51434640/214507732-34d02b93-c41e-48e5-90e7-46c4be0627f7.png">

2. Select **Enable** to add the Cloud Vision API to your project.

<img width="1254" alt="Enabling Cloud Vision API (1)" src="https://user-images.githubusercontent.com/51434640/214509795-440c3804-c8c9-4ba0-8749-f209239c7485.png">

### 3. Create Cloud Vision credentials

1. On the **APIs & Services** screen, select **Credentials** > **Create credentials** > **Service account**.

<img width="1163" alt="CreatingCloud Vision credentials (1)" src="https://user-images.githubusercontent.com/51434640/214512446-06087d86-120f-4bf2-aded-8d8b8ae5a0aa.png">

2. Add a **service account name** and select **done**.

<img width="1149" alt="Adding account name" src="https://user-images.githubusercontent.com/51434640/214513614-d109f355-49a1-480d-997b-b854d94b4a5a.png">

3. Select the **service account email address** to open details about it.
 
<img width="1201" alt="Opening the account details" src="https://user-images.githubusercontent.com/51434640/214514534-fa56e0d9-714d-4f71-b0a2-6f684782b069.png">

4. Select **Keys** > **Add key** > **Create new key**.

<img width="1200" alt="Creating a new key" src="https://user-images.githubusercontent.com/51434640/214518109-f7cec69e-0dbb-41be-acdb-3ab5a00d32dd.png">

5. Then with **JSON** chosen, select **Create** to create a new key.

<img width="1196" alt="Creating a new key (1)" src="https://user-images.githubusercontent.com/51434640/214519067-2487870d-56fc-4258-a474-362d52ab4ed6.png">

Google will send you a `.json` file. This is your key for the ORC Pipeline.

Congratulations! Now you are ready to use the [OCR Pipeline](https://tools.openpecha.org/pipelines/).

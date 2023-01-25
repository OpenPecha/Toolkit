
# OP Pipeline

## What is the OP Pipeline and how does it work?

The OP Pipeline provides an interface for users to select scans from the BDRC library and OCR them. 

Given a BDRC scan number, the OP Pipeline:

1. Retrieves the scans that make up the text from the [BDRC library](https://library.bdrc.io).
2. OCRs them with [Google Cloud Vision](https://cloud.google.com/vision).
3. Converts the results into the [OPF format](#) using the OpenPecha toolkit.
4. Creates a new repo on [OpenPecha Data's GitHub](https://github.com/OpenPecha-Data).
5. Puts the OPF files for the text into the new repo.

## How to use the OP Pipeline

> **Note**: Using the OP Pipeline requires a Google Cloud Vision key. Learn how to get one [here].

### Name

In this field, you can name the batch that you are scanning.

### Inputs

The OP Pipeline currently only supports OCRing images in the BDRC library. Texts are retrieved using their BDRC scan ID.

Example of a BDRC scan ID:

<img width="1473" alt="BDRC scan ID" src="https://user-images.githubusercontent.com/51434640/214571073-7d28e042-228f-4904-80cc-c487cc1fdeb0.png">

The scan ID follows `bdr:`. In this case, the ID is `W1KG12304`.

Multiple scans can be OCRd in one batch. Add one BDRC scan ID per line.

> **Warning**: BDRC Work IDs and Version IDs aren't supported. If used, the job will result in failure.

### OCR Engine

The OP Pipeline currently only supports Google Cloud Vision.

### Model Type

These model types are accessible by the OP Pipeline.

- builtin/stable
- builtin/latest
- builtin/weekly

`builtin/weekly` seems to produce the best results, but this needs more testing. Feel free to experiment.

> **Warning**: `builtin/stable` doesn't currently work for Tibetan.

### Language Hint

The OP Pipeline can use the language hints listed below.

- Auto
- Tibetan
- Tibet-handwriting
- Chinese
- Chinese-hanwriting
- Devanagari
- Davenagari-handwriting

`Auto` seems to produce the best results, but this needs more testing. Feel free to experiment.

### Google Cloud Service Account Key 

The key for the OP Pipeline is the `.json` file from Google Cloud when you 

Open it in a text editor and copy the body of the file into this field.

> **Note**: If you don't have a key or need help getting one, read this [guide](#).

### Sponsor name

The could be your name, your organization's name, or the person who bought the Google Cloud credit used to OCR the text(s) in this job. The name gets added to the OPF metadata. 

### Allow BDRC and OpenPecha to use the results for improving this service.*

By ticking this box, the results get put in a public [OpenPecha Data repository](https://github.com/OpenPecha-Data) on GitHub and you agree to allow BDRC and OP to use the resulting data.

If you don't agree to share the data, the file will be put in a private repo on OpenPecha Data's GitHub. In this case, after your job is successfully completed, email us at openpecha[at]gmail.com for access.

## Processing the OCRs

After you fill out the form, select **Start**. The job may take up to several minutes.

## All Batches

On the right side of the Op Pipeline interface is a list of all of the batches that have been processed. Select **Details** next to your batch to see its progress and results.

## Batch Details

Here you can:

- Select the link under **Results** to go to the repo that contains the OCRd file.
- Toggle the chevron next to **Inputs** to see the list of files that were OCRd
- Toggle the chevron next to **Pipeline Config** to see the language hints, model type, and engine that were used.
- Select **Details** under Actions to see more metadata about the batch.

<img width="1031" alt="Batch details" src="https://user-images.githubusercontent.com/51434640/214577513-36560227-0c92-482d-b2d8-70758a38e7b2.png">

### Need help?

* Email us at openpecha[at]gmail.com.
* File an [issue](https://github.com/OpenPecha/Data-Pipeline-Manager/issues/new?assignees=&labels=&template=bug_report.md&title=).
* Join our [Discord](https://discord.com/invite/7GFpPFSTeA) and ask there.



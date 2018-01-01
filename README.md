# Google App Engine Blobstore Blob Management Tool

This is not an officially supported Google product.

This tool provides a graphic user interface that can be used to manage
blobs stored in the Google App Engine
[Blobstore API](https://cloud.google.com/appengine/docs/standard/python/blobstore/).

**Note:** this library is written in Python, but because it is a stand-alone
service, it can be used on any App Engine application.

## Getting Started

These instructions will deploy a new App Engine service to your project,
called `blob-management`.
The endpoints of the service are configured as `login: admin`, so only users
of your project will be able to access them. The default automatic scaling is
used, so the service will scale to 0 when not in use.

To deploy, use the following:

```
$ gcloud auth login
$ gcloud config set project [your-project-id]
$ gcloud app deploy src/app.yaml
```

When the deployment is complete, you can access the tool at the following
location:

```
https://blob-management-dot-[your-project-id].appspot.com
```

Browse the blobs, sorting and filtering as you wish. Use the Next Page
button to move through pages.
Click the blob filename to download the blob.
Select the blobs you want to delete and click the Delete button.
**Note that this is a permanent deletion and cannot be reversed!**


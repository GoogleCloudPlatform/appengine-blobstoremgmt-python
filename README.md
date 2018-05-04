# Google App Engine Blobstore Blob Management Tool

## 🚨🚨🚨 Disclaimer 🚨🚨🚨
This is not an officially supported Google product and will not be
continually maintained. This tool is an App Engine app run by a
customer, and therefore has no SLA.

## Introduction
This tool provides a graphic user interface that can be used to manage
blobs stored in the Google App Engine
[Blobstore API](https://cloud.google.com/appengine/docs/standard/python/blobstore/).

Features include:

 - Browse blobs, including sorting, filtering, and pagination
 - "Click to download" of blobs
 - Individual and bulk deletion

**Note that deletion is a permanent action and cannot be reversed!**

## Getting Started

These instructions will deploy a new App Engine service to your project,
called `blob-management`.

To deploy, run the following commands:

```bash
$ gcloud auth login
$ gcloud config set project [your-project-id]
$ gcloud app deploy src/app.yaml
```

When the deployment is complete, you can access the tool at the following
location:

```
https://blob-management-dot-[your-project-id].appspot.com
```

**Note:** While this app is written in Python, because it is a stand-alone service,
it can be used to manage blobs in any App Engine application, using any runtime.

## Application security

The endpoints of the service are configured as `login: admin`, so only certain
users in your project will be able to access them. By default, all project
Owners, Editors, and Viewers, as well as users with the App Engine Admin role
will have access.

**Note:** because of the above, this means that project Viewers will be able to
create, update, and delete blobs rather than simply being able to view them. If this
is not desired behavior, you can modify the `blob-management` service to implement
additional fine-grained authorization.

## Cost

Running this app will incur some additional costs as it uses standard environment instances
and may generate outgoing network bandwidth (e.g. downloading a blob). Details on App Engine
pricing can be found [here](https://cloud.google.com/appengine/pricing). 

**Note:** the default automatic scaling is used, so the service will scale to 0 when not in use.


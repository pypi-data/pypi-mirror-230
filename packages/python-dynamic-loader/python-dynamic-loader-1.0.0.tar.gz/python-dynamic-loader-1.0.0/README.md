# Dynamic Class Loader

One of the issues developers can encounter when developing in Python is the
time taken to deploy changes. You can help reduce this time by dynamically
loading some of your Python classes. This allows you to make iterative changes
to just the area of your application that you’re working on.

For example, if you’re creating code that requires lots of small changes and
want to see your results quickly, without needing to redeploy the
Cloud Function each time, then this solution is for you. Put the code you
want to change in a class you can dynamically load, and redeploy the Cloud
Function once calling this new class. You can now copy the new class to your
chosen storage and test iteratively by just changing the file in storage without
having to redeploy the Cloud Function.

## Installation and Setup

The library is available on PyPi as `python-dynamic-loader`. To install it
into your local python environment, simple add the following line to your
`requirements.txt`:

> `python-dynamic-loader>=1.0.0`

## Usage

The system relies on the classes extending the `DynamicClass` object, which has
in it the loader, and suggests a method to override to make generic loading
easier.

### How to create a dynamically loadable class

A very simple example can be found in the `command_files` folder.

```python
  1 from typing import Mapping
  2 from dynamic import DynamicClass
  3
  4
  5 class HelloWorld(DynamicClass):
  6 """A simple dynamic Hello World."""
  7
  8 def run(self, **attributes: Mapping[str, str]) -> str:
  9  """Runs the command.
 10
 11  The is the mandatory implementation of the `run` method in
 12  `DynamicClass`. It is the only method that the framework will call.
 13
 14  The attributes are passed as Python keyword args and will vary
 15  according to whatever the user needs.
 16
 17  Returns:
 18     Dict[str, Any]: the result of the command
 19  """
 20  return "Hello world!"
```

So your named class must extend `DynamicClass`, as shown on line 5.

You should then implement the `run` method, which at a minimum should return the
result of the class. This `run` method is only a placeholder, you could create
any method you want.

Once this is done, you need to call the code when needed.

```python
  1 import dynamic
  2
  3 processor = DynamicClass.install(module_name='my_module',
  4                                  class_name='HelloWorld',
  5                                  storage=dynamic.CloudStorage,
  6                                  bucket='my-gcs-bucket')
  7 processor().run()
```

As you can see, the first step is to `install` the new class. This loads the
code from the chosen storage location (`dynamic.CloudStorage` in this example)
and returns the `class` object.

`install` takes 3 mandatory parameters and any number of optional ones that will
be passed on to the storage object.

<a href="#install"></a>

| Parameter | Function  |
|:-:|-|
|module_name|The name of the file (module) the code is in, without any extension. This can be any valid Python name. <br/> **NO  dot (`.`) characters are permitted.**|
|class_name|The name of the class within the file to be used. A `class` object will be returned that can then be instantiated by the user.|
|storage|The storage to use. Provided examples are listed [below](#provided-sourcegrabbers).|
|_other_|Any other named parameters will be passed to the constructor of the `SourceGrabber`. <br/>In the example above, `bucket` is passed to `dynamic.CloudStorage`,.|

You can then instantiate the object (`processor()`) and call the run method, or
any other method you have defined.

The module is reloaded each time, so the latest version will always be used.

## Where To Store Your Code: `SourceGrabber`s

### Provided `SourceGrabber`s

#### `CloudStorage`

This is to grab the code from a bucket in Google Cloud Storage (GCS).
`CloudStorage` takes one parameter:

| Parameter | Function  | Default |
|:-:|-|:-:|
|`bucket`|The name of the GCS bucket in which the code files are stored.|`dynamic-commands`|

The files must be stored in the bucket, with the `.py` extension as normal text
files. As an example, the above sample code would be stored as `hello.py`, like
this:


#### `SecretManager`

This fetches the code from a secret stored in Google Secret Manager in plain
text. It takes no additional parameters.

The file is uploaded as a secret to secret manager with the name of the module
just as is. For example, the above sample code would be stored in Secret Manager
as a `secret` called "`hello`", and the value of the secret should be the text
content of the class. Your Secret Manager should look like this:

Secret Manager can store up to 64kb of text which sdhould be large enough for
most uses.

#### `LocalStorage`

Mostly useful for testing, this is to grab the code from a local folder on the
user's local drive.
`LocalStorage` takes one parameter:

| Parameter | Function  | Default |
|:-:|-|:-:|
|`folder`|The name of the local folder in which the code files are stored.|None|

The files must be stored in the folder, with the `.py` extension as normal
source files. As an example, the above sample code would be stored as
`hello.py`.

### Creating your own `SourceGrabber`

Any location where you can fetch plain text from can be used as a source for the
code to be loaded dynamically - Amazon S3, Fiurestore, Big Query etc. would all
be decent choices.

In order to create a `SourceGrabber` you need to create a class extending
`dynamic.SourceGrabber`.

It must implement at a minimum the `fetch_source`
method, which must return the source to be loaded as a `str`.

It can, in addition, include an `__init__` method which will be passed any
additional startup parameters given to the `install` method
([see above](#install)). If you intend to do this, remember to always include
the `**unused` as the final parameter so that unexpected parameters will not
cause instantiation failures.

Examples of `SourceGrabber`s can be seen in the `dynamic.source_grabbers`
module.

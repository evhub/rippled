The basic rudiments for these instructions came from here:

http://hiltmon.com/blog/2013/07/05/xcode-and-the-simple-c-plus-plus-project-structure/

These instructions are dependent on two files that I've not pushed to the
main build.  They are:
  SConstruct (minor modifications)
  xcode_invoke_scons (a bash script that helps the environment)
These need to be in the root of your rippled tree for these instructions
to work.

The xcode_invokes_scons script is required because Xcode doesn't bring in
the environment that is set up for your bash command line.

Your copy of xcode_invokes_scons will need to be tweaked for your environment.
In particular, fix the BOOST_ROOT to point at the boost installation that
you're using for RippleD.  It should be the same as the value you've set in
your bash environment.

Make sure that the xcode_invokes_scons script has execute permissions for
all groups.  In some cases git does not preserve file permissions.
$ chmod +x xcode_invokes_scons

The Xcode low-level debugger, lldb, has trouble finding symbols is a unity
build (where a *.cpp includes a *.cpp).  To help lldb with that you need to
create a "~/.lldbinit" file in your home directory.  Put the following contents
in the .lldbinit file:


# setting this value because the rippled unity build screws up lldb
# finding symbols.  See here...
#
# http://lldb.llvm.org/troubleshooting.html
#
settings set target.inline-breakpoint-strategy always


This will slow down lldb finding symbols, but it will find them more reliably.

We're going to create a brand new Xcode project for RippleD.  So if you have
a previously existing Xcode project for RippleD, we'll need to remove (or
at least rename) the old one.  Go ahead and do that now.

Install Xcode if you haven't done so already.

Start Xcode from the Launchpad

Select "Create a new Xcode project"

Choose a template.  Select OS X -> Other -> External Build System
Click Next

Choose options for our project.  Type in:
  Product Name:       rippled
  Organization Name:  Ripple Labs
  Company Identifier: ripplelabs
  Build Tool:         /Users/<your path>/xcode_invokes_scons
Click Next

Xcode wants to create a new directory named "rippled" where it will put
the Xcode project.  Go ahead and let it do that.  This means we'll have
to mv the project in a minute.  For now in the dialog navigate to the
directory where you have already extracted rippled.
Click Create.

Now close Xcode.  We're about to move the xcodeproj to the right place.

In a terminal window 'cd' to your rippled directory.  You'll see an additional
rippled directory inside it.  'cd' into this second rippled directory.

$ mv rippled.xcodeproj ..
$ cd ..
$ rmdir rippled

Now we want to make it easy to get the source files into the Xcode project
while not picking up any generated files.  So while were here execute the
command

$ scons -c

Now we can finish configuring the Xcode project.  Open Xcode again.  This
time click Open Other.

In the opened dialog navigate to and select the rippled.xcodeproj in your
rippled directory.
Click Open.

You'll see the External Build Tool Configuration.  We need to patch that up.
  Build Tool: /Users/<your path>/rippled/xcode_invokes_scons
  Arguments:  <None>
  Directory:  /Users/<your path>/rippled
With these settings Xcode will only be able to build the debug version of
rippleD.  I'm good with that for this stage.

Now go up to the menu bar for Xcode.  Click File then "Add Files to 'rippled'"
Navigate to rippled/src.  Select 'src'.
Click Add.

Before we can debug anything we need to build the target.
Click <command>B to build.

Now we need to fix up the debug target.  Go up the the Xcode menu bar and
click Product -> Scheme -> Edit Scheme...

In the resulting dialog click on Executable -> Other...

Navigate to the rippled/build/rippled executable file.  Select that file and
Click Choose.

Click Okay.

Click Run.

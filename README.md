# Plastic

There is a reason that the most difficult problem in computer science is naming
things. The goal of programming language design is to make the work of a
programmer less technical and more philosophical.

Plastic is an open source programming language that magically solves all of
your problems. It strives not to suck; which it accomplishes to varying
degrees. No unicorns were injured in its creation or ongoing development.

I realise this description of plastic is of almost no use to you. I will write
something better eventually. In the meantime, you can take a look at the
plastic programs in `programs/`.

# Practicals

There are two parts to this project. A bytecode interpreter that uses the pypy
infrastructure (and so is written in rpython) and a compiler that is just
straight python.

To get started, you'll need to checkout pypy:

    hg clone https://bitbucket.org/pypy/pypy

And (in this project) copy the config file:

    cp config_example.sh config.sh

And edit it to point to your pypy checkout. Then you can build the interpreter
with `./build.sh`. You can compile things with `./compile [input] [output]`.

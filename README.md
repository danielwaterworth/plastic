# Plastic

There is a reason that the most difficult problem in computer science is naming
things. The goal of programming language design is to make the work of a
programmer less technical and more philosophical.

Plastic is an open source programming language that magically solves all of
your problems. It strives not to suck; which it accomplishes to varying
degrees. No unicorns were injured in its creation or ongoing development.

# Practicals

There are two parts to this project. A bytecode interpreter that uses the pypy
infrastructure (and so is written in rpython) and a compiler that is just
straight python.

To get started, you'll need to checkout pypy:

    hg clone https://bitbucket.org/pypy/pypy

You'll also need to install the dependencies:

    pip install -r requirements.txt

And (in this project) copy the config file:

    cp config_example.sh config.sh

And edit it to point to your pypy checkout. Then you can build the interpreter
with `./build.sh`. You can compile things with `./compile [input] [output]`.

# Hello, world

hello.plst:

```ruby
import printer

service Test(p : printer.Printer)
    constructor new()
    end

    implements EntryPoint
        define main() -> Bool do
            @p.print("hello, world");
            return true;
        end
    end
end

entry
    p := printer.SysPrinter().new();
    return Test(p).new();
end
```

Then:

    ./compile hello.plst hello.bc
    ./main-c exec hello.bc

## Extras

You can view the bytecode produced with:

    ./print_bc hello.bc

You can build a trace of all of the system calls with:

    ./main-c trace hello.bc hello.trace

And you can re-run the program by replaying the system calls with:

    ./main-c replay hello.bc hello.trace

This isn't useful unless you use the `debug` function that takes a string. You
can rerun a program with a trace using different bytecode. This allows you to
add debug calls to a program's execution after the fact.

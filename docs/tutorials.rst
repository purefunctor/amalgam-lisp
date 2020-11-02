Tutorials
=========

Creating Macros
---------------

Macros are a flexible way to define new language constructs within
the language. This tutorial implements a `for-each` loop as an example.

First, let's define the form of our `for-each` loop:

.. code-block:: lisp

    (for target in vector expression)

:data:`target` is the name of the symbol, :data:`vector` is the
sequence we're iterating through, and :data:`expression` being the
actions performed for every iteration.

We can use the :data:`macro` function to define this form:

.. code-block:: lisp

    (macro for [target in vector expression]
           (do (setn vector (eval vector))
               (setn index 0)
               (setn final (len vector))
               (loop (when (= index final) (break))
                     (setr target (at index vector))
                     (eval expression)
                     (setn index (+ index 1)))))

Analysing this example, two procedures are to be observerd,
specifically, the use of :data:`setr` and :data:`eval`. First, the
:data:`vector` that is passed to the macro contains unevaluated
expressions that first have to be evaluated using :data:`eval`. As
described by the form that we've written earlier, :data:`target` is
the name of the symbol that we're assigning to, and as such, we'll
have to use :data:`setr` instead of :data:`setn` to make sure that
we're not binding using :data:`target` literally. We then evaluate the
:data:`expression` literal, which has access to the value bound to
:data:`target`.

Let's test it out on the REPL:

.. code-block:: lisp

    > (macro for [target in vector expression]
    |        (do (setn vector (eval vector))
    |            (setn index 0)
    |            (setn final (len vector))
    |            (loop (when (= index final) (break))
    |                  (setr target (at index vector))
    |                  (eval expression)
    |                  (setn index (+ index 1)))))
    for
    > (for x in [1 2 3 4 5]
    |      (print (* x x)))
    1
    4
    9
    16
    25
    :NIL

The newly defined :data:`for` macro is able to iterate through the
vector, binding each number to :data:`x` before evaluating the
expression.

Note: Macros create their own closure, and symbols bound
within them are inaccessible after evaluation.

Modifying the macro to return the expression evaluated last is left
as an exercise for the reader.

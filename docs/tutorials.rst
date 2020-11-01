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

    (macro for (qtarget in qvector qexpression) ...)

:data:`target`, :data:`vector`, and :data:`expression` are prefixed
with :data:`q` as Arguments to macros are passed literally as quoted
values and are not evaluated, giving the macro the ability to
selective unquote and evaluate expressions.

Let's now define what happens within the macro:

.. code-block:: lisp

    (macro for (qtarget in qvector qexpression)
           (do (setn target (unquote qtarget))
               (setn vector (unquote qvector))
               (setn expression (unquote qexpression))
               (setn index 0)
               (setn final (len vector))
               (loop (when (= index final) (break))
                     (setr target (at index vector))
                     (eval expression)
                     (setn index (+ index 1)))))

The values being manipulated in the macro are first unquoted and bound
to names without their :data:`q` prefix:

.. code-block:: lisp

    (do (setn target (unquote qtarget))
        (setn vector (unquote qvector))
        (setn expression (unquote qexpression)))

Then, the looping logic is defined:

.. code-block:: lisp

    (setn index 0)
    (setn final (len vector))
    (loop (when (= index final) (break))
          (setr target (at index vector))
          (eval expression)
          (setn index (+ index 1)))

Two things are to be observed here, specifically, the use of
:data:`setr` and :data:`eval`. As described by the form that we've
defined earlier, :data:`target` is the name of the symbol that
we're assigning to, and as such, we'll have to use :data:`setr` instead
of :data:`setn` to make sure that we're not binding to :data:`target`
literally. We then evaluate the :data:`expression` literal, which then
has access to the value bound to :data:`target`.

Let's test it out on the REPL:

.. code-block:: lisp

    > (macro for (qtarget in qvector qexpression)
    |        (do (setn target (unquote qtarget))
    |            (setn vector (unquote qvector))
    |            (setn expression (unquote qexpression))
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

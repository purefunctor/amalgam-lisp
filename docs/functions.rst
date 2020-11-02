Functions
=========

Documentation for the various built-in functions.

Arithmetic
----------

.. function:: (+ e0 e1 ... en)

   Performs a summation of the provided expressions.

.. function:: (* e0 e1 ... en)

   Performs a multiplication of the provided expressions.

.. function:: (- e0 e1 ... en)

   Subtracts :data:`e0` by the sum of :data:`e1 ... en`.

.. function:: (/ e0 e1 ... en)

   Divides :data:`e0` by the product of :data:`e1 ... en`

Boolean
-------

.. function:: (bool e)

   Checks for the truthiness of an expression

.. function:: (not e)

   Checks for the falsiness of an expression

.. function:: (and e0 e1 ... en)

   Evaluates and reduces the expressions using an `and` operation,
   short-circuiting evaluation when a falsy value is encountered.

.. function:: (or e0 e1 ... en)

   Evaluates and reduces the expressions using an `or` operation,
   short-circuiting evaluation when a truthy value is encountered.

Control
-------

.. function:: (if condition then else)

   Basic branching construct. If :data:`condition` evaluates to a
   truthy value, evaluates :data:`then`, otherwise, evaluates
   :data:`else`.

.. function:: (when condition then)

   Synonym for :data:`if` where :data:`else` defaults to :data:`NIL`.

.. function:: (cond [[condition value] ...])

   Traverses pairs of conditions and values. If the condition
   evaluates to a truthy value, returns the provided value,
   short-circuiting evaluation. Returns :data:`NIL` when no
   conditions are met.

.. function:: (do expression...)

   Evaluates each expression, returning what was evaluated last.

.. function:: (loop expression...)

   Evaluates each expression, looping back at the end. Can be
   broken by the :data:`return` and :data:`break` functions.

.. function:: (return expression)

   Breaks out of a loop evaluating to a value.

.. function:: (break)

   Breaks out of a loop evaluating to :data:`NIL`.

Comparison
----------

.. function:: (> x y)

   Performs a `greater than` operation.

.. function:: (< x y)

   Performs a `less than` operation.

.. function:: (= x y)

   Performs a `equal to` operation.

.. function:: (/= x y)

   Performs a `not equal to` operation.

.. function:: (>= x y)

   Performs a `greater than or equal to` operation.

.. function:: (<= x y)

   Performs a `less than or equal to` operation.

IO
--

.. function:: (print expression)

   Prints an :data:`expression`.

.. function:: (putstrln string)

   Prints the contents of a :data:`string`.

.. function:: (exit code)

   Stops the execution of the program.

Meta
----

.. function:: (require module-path)

   Loads a module given its :data:`module-path`, importing the exposed
   symbols to the current environment with respect to the export list
   created by :data:`provide`.

.. function:: (provide symbols...)

   Creates an export list of :data:`symbols` when loaded through
   :data:`require`.

.. function:: (setn name value)

   Lexically binds a literal :data:`name` to a :data:`value`.

.. function:: (setr name-ref value)

   Lexically binds an evaluated :data:`name-ref` to a :data:`value`.

.. function:: (unquote qexpression)

   Unquotes a given :data:`qexpression`.

.. function:: (eval expression)

   Fully evaluates an :data:`expression`, optionally removing a layer
   of quoting.

.. function:: (fn [args...] body)

   Creates a scoped lambda given a vector of :data:`args`, and a
   :data:`body`. Binds to a closure when created inside of one.

.. function:: (mkfn name [args...] body)

   Creates a scoped function given a :data:`name`, a vector of
   :data:`args`, and a :data:`body`. Binds to a closure when created
   inside of one.

.. function:: (macro name [args...] body)

   Creates a scoped macro given a :data:`name`, a vector of
   :data:`args`, and a :data:`body`. Binds to a closure when created
   inside of one.

.. function:: (let [[name value]...] body)

   Creates a closure where each :data:`value` is bound to a
   :data:`name` before evaluating :data:`body`.

String
------

.. function:: (concat s0 s1 ... sn)

   Concatenates strings together.

Vector
------

.. function:: (merge v0 v1 ... vn)

   Merges vectors together.

.. function:: (slice vector start stop step)

   Slices a :data:`vector` using :data:`start`, :data:`stop`, and
   :data:`step`.

.. function:: (at index vector)

   Returns an item from a :data:`vector` given its :data:`index`.

.. function:: (remove index vector)

   Removes an item from a :data:`vector` given its :data:`index`.

.. function:: (len vector)

   Returns the length of a :data:`vector`.

.. function:: (cons item vector)

   Prepends an :data:`item` to a :data:`vector`.

.. function:: (snoc vector item)

   Appends an :data:`item` to a :data:`vector`.

.. function:: (is-map vector)

   Verifies if the :data:`vector` is a map.

.. function:: (map-in vector atom)

   Checks whether :data:`atom` is a member of :data:`vector`.

.. function:: (map-at vector atom)

   Obtains the value bound to :data:`atom` in :data:`vector`.

.. function:: (map-up vector atom value)

   Sets or updates the :data:`atom` member of :data:`vector`
   with :data:`atom`.

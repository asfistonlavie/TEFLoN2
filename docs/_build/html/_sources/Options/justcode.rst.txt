Just Code
=========
Key Goals
---------

Options
-------


Scratch
~~~~~~~

KidsRuby
~~~~~~~~

Python
~~~~~~

He is some code:

.. code-block:: python
   :emphasize-lines: 3,5

   def some_function():
       interesting = False
       print 'This line is highlighted.'
       print 'This one is not...'
       print '...but this one is.'

And here is some Python code just in case you wanted to see it:

.. code-block:: python

	def cigarParse(cig):
	    operation = ['M','I','D','N','S','H','P','=','X']
	    opValue = [0,0,0,0,0,0,0,0,0]
	    for i in range(1):
	        arr = cig.split(operation[i])
	        for j in range(len(arr)):
	            if arr[j].isdigit():
	                opValue[i] += int(arr[j])
	                arr[j]=''
	            else:
	                for k in range(len(operation)):
	                    switch =1
	                    arr2 = arr[j].split(operation[k])
	                    for l in range(len(arr2)):
	                        if arr2[l].isdigit() and switch ==1:
	                            opValue[k] += int(arr2[l])
	                            switch =0
	                        elif arr2[l].isdigit() and switch ==0:
	                            opValue[i] += int(arr2[l])
	    return opValue

Hopscotch
~~~~~~~~~
aikit
=====

一些ai开发过程中使用到的工具模块

-  `aikit <#aikit>`__

   -  `安装 <#安装>`__
   -  `使用 <#使用>`__

      -  `aos <#aos>`__

安装
----

.. code:: commandline

   git clone git@github.com:cpcgskill/aikit.git

使用
----

aos
~~~

.. code:: python

   import os

   # 设置以下环境变量为腾讯云cos的配置

   os.environ['COS_Region'] = 'ap-hongkong'
   os.environ['COS_SecretId'] = ''
   os.environ['COS_SecretKey'] = ' '
   os.environ['COS_Bucket'] = ' '

   import torch
   from aidevkit.aos import Saver


   class MyModule(torch.nn.Module):
       def __init__(self):
           super(MyModule, self).__init__()
           self.linear = torch.nn.Linear(10, 10)
           self.s = 1

       def forward(self, x):
           return self.linear(x)


   saver = Saver(lambda: MyModule(), 'test.pt', 3)
   for i in range(10):
       saver.step()

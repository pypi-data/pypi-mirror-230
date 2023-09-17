from setuptools import setup

setup(name='updns',
      version="1.0",
      description="用于更新'home.w0rk.top'的域名Ip到hosts解析",
      keywords='python、PyPi source、terminal',
      author='sanfeng',
      author_email='2669291603@qq.com',
      packages=["dns"],
      entry_points={
          'console_scripts': [
              'updns = dns.dns:main'
          ]
      },
      )

from setuptools import setup, find_packages
setup(
    name='zhudengjideku', # 包名
    version='0.2', # 版本号
    description='用于文字转语音', # 描述
    author='xzk', # 作者
    author_email='2367574471@qq.com', # 作者邮箱
    packages=find_packages(), # 需要打包的子包，可以自动发现
    install_requires=[ # 依赖库
        'numpy',
        'pandas'
    ],
    entry_points={ # 入口脚本
        'console_scripts': [
            'your-cli-command=your_module:main',
        ],
    },
    classifiers=[ # 分类器
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.6', # Python版本要求
)
import setuptools
with open("Discription.md", "r",encoding="utf-8") as f:
    long_description = f.read()
    
setuptools.setup(
    name = "chatGPT_automator",
    version = "0.1.1",
    author = "evinljw",
    author_email="evin92@gmail.com",
    description="Regarding automating ChatGPT using Selenium in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/kevinljw/chatgpt_automator",
    packages=setuptools.find_packages(),     
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'selenium==4.9.0',
        'webdriver_manager>=4.0.0'
    ]
    )
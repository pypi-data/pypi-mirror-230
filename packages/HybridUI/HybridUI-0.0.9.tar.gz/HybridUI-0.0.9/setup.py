import setuptools

with open("./README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="HybridUI", 
    version="0.0.9",
    author="Ari Bermeki",
    author_email="ari.bermeki.de@gmail.com",
    description="Create an efficient and enjoyable work experience with pure Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AriBermeki/hybridui",
    packages=setuptools.find_packages(),
    package_data={
        "hybrid": ["charts/*", "core/*", "elements/*", "eventarguments/*", "libary_images/*", "static/**","templates/*"]
    },
    install_requires=[
        'fastapi',
        'fastapi_socketio',
        'python-socketio',
        'uvicorn[standard]',
        'psutil', 
        'python-dateutil', 
        'python-multipart',
        'jinja2',
        'aiofiles',
        'starlette'
    ],
    include_package_data=False,
    extras_require={
        "full": [
            "graphene",
            "itsdangerous",
            "pyyaml",
            "requests",
            "orjson",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP"
    ],
    python_requires='>=3.9'
)


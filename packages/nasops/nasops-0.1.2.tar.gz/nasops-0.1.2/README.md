0. rm -rf nasops.egg-info dist build
1. python3 setup.py sdist bdist_wheel --universal
2. python3 -m twine upload --verbose dist/*


## support ops:  
1. download file 
`dtools download --url xxxxxx`   
1. upload file / dir  
`dtools upload --name wangyang.zuo --password xxxxxx --local_dir xxxx --nas_dir xxxx`   
1. list file / dir 
`dtools list--name wangyang.zuo --password xxxxxx --nas_dir xxxx`   



添加了分享文件的功能，但是有一个日期限制只有30天的时间限制
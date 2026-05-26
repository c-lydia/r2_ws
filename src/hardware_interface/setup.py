from setuptools import find_packages, setup

package_name = 'hardware_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lydia-chheng',
    maintainer_email='chhenglydiacl@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'can_driver_node = hardware_interface.can_driver:main',
            'hfi_a9_node = hardware_interface.hfi_a9:main',
            'inverse_kinematic_node = hardware_interface.inverse_kinematic:main',
            'odometry_node = hardware_interface.odometry:main'
        ],
    },
)

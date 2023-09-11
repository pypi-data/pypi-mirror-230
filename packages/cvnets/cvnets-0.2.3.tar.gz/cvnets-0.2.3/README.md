# Tutorial for Computer Vision AI tasks

## Prerequisite

```bash
$ conda create -n cvnets python=3.8 -y
$ conda activate cvnets
$ (cvnets) conda install pytorch=1.13.0 torchvision=0.14.0 -c pytorch -y
# $ (cvnets) pip install -r requirements.txt
```

# Tutorial

## [1. Classification](./recognition_models/classification)

- [1.1 Binary Classification](./recognition_models/classification/binary_classification)
- [1.2. Multi-Class Classification](./recognition_models/classification/multi_class_classification)
- [1.3. Multi_Label Classification](./recognition_models/classification/multi_label_classification)

twine upload --repository-url https://test.pypi.org/legacy/ dist/*




### Etc

1. jupyter notebook kernel install
    ```
    $ conda install jupyter
    $ python -m ipykernel install --user --name cvnets
    ```

### Reference
- https://rwightman.github.io/pytorch-image-models
- https://github.com/KevinMusgrave/pytorch-metric-learning
- 
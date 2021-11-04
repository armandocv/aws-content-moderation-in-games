## Package Layer

```
rm deployment.zip && \
cd python && \
cp -r ../env/lib/python3.9/site-packages/* . && \
cd ../ && \
zip -r layer.zip python
```

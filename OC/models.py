from django.db import models
from django.db.models.base import ModelState

# Create your models here.
class OrdenDeCompra(models.Model):
    cliente = models.CharField(max_length=30)
    proveedor = models.CharField(max_length=30)
    _id = models.CharField(primary_key=True, editable=False, max_length=100)
    sku = models.IntegerField()
    fechaEntrega = models.DateTimeField(auto_now=False, auto_now_add=False)
    cantidad = models.IntegerField()
    cantidadDespachada = models.IntegerField()
    precioUnitario = models.IntegerField()
    canal = models.CharField(max_length=10)
    estado = models.CharField(max_length=10)
    notas = models.CharField(max_length=100)
    rechazo = models.CharField(max_length=100)
    anulacion = models.CharField(max_length=100)
    urlNotificacion = models.CharField(max_length=200)
    en_produccion = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

class Test(models.Model):
    name = models.CharField(max_length=4)

class Contador(models.Model):
    sku = models.IntegerField()
    tick = models.IntegerField(default=0)
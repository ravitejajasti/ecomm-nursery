import random
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator, \
    MaxValueValidator

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

from ecommerce.aws.download.utils import AWSDownload
from ecommerce.aws.utils import ProtectedS3Storage
from ecommerce.utils import unique_slug_generator, get_filename


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    # print(instance)
    #print(filename)
    new_filename = random.randint(1,3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "products/{new_filename}/{final_filename}".format(
            new_filename=new_filename, 
            final_filename=final_filename
            )

class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) | 
                  Q(description__icontains=query) |
                  Q(price__icontains=query) |
                  Q(tag__title__icontains=query)
                  )
        # tshirt, t-shirt, t shirt, red, green, blue,
        return self.filter(lookups).distinct()

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self): #Product.objects.featured() 
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id) # Product.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


#Testing Comments section Ravi.


class Comment(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete= 'models.DO_NOTHING')
    # product     = models.ManyToManyField(Product, default=True)
    # url         = models.URLField(null=True) # not a path, full url http://www.srvup.com/projects/1
    content     = models.TextField()
    #image       = models.ImageField()
    allow_annon = models.BooleanField(default=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    RATING_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        )
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    
    def __str__(self):
        return self.content

    # @property
    # def owner(self):
    #     return self.user
 
    
class Product(models.Model):
    title           = models.CharField(max_length=120)
    slug            = models.SlugField(blank=True, unique=True)
    description     = models.TextField()
    price           = models.DecimalField(decimal_places=2, max_digits=20, default=39.99)
    discount        = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=39.99)
    image           = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_digital      = models.BooleanField(default=False) # User Library
    low_maintenance = models.BooleanField(default=False)
    medicinal       = models.BooleanField(default=False)
    air_purifier    = models.BooleanField(default=False)
    flowering       = models.BooleanField(default=False)
    fruit_plant     = models.BooleanField(default=False)
    insect_repllenet= models.BooleanField(default=False)
    holy            = models.BooleanField(default=False)
    cactus_n_succ   = models.BooleanField(default=False)
    creepers        = models.BooleanField(default=False)
    herbs           = models.BooleanField(default=False)
    indoor          = models.BooleanField(default=False)
    miniatures      = models.BooleanField(default=False)
    is_digital      = models.BooleanField(default=False)
    is_digital      = models.BooleanField(default=False)
    seasonal        = models.BooleanField(default=False)
    ferns           = models.BooleanField(default=False)
    office          = models.BooleanField(default=False)
    balcony         = models.BooleanField(default=False)
    comments        = models.ManyToManyField('Comment')


    objects = ProductManager()

    def get_absolute_url(self):
        #return "/products/{slug}/".format(slug=self.slug)
        return reverse("products:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    @property
    def name(self):
        return self.title

    def get_downloads(self):
        qs = self.productfile_set.all()
        return qs
    # Ravi's - Calculating after discount price
    @property
    def finalprice(self):
        return (self.price)*(1-self.discount)

    # End Ravi's - Calculating after discount price


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=Product) 


def upload_product_file_loc(instance, filename):
    slug = instance.product.slug
    #id_ = 0
    id_ = instance.id
    if id_ is None:
        Klass = instance.__class__
        qs = Klass.objects.all().order_by('-pk')
        if qs.exists():
            id_ = qs.first().id + 1
        else:
            id_ = 0
    if not slug:
        slug = unique_slug_generator(instance.product)
    location = "product/{slug}/{id}/".format(slug=slug, id=id_)
    return location + filename #"path/to/filename.mp4"



class ProductFile(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
    name            = models.CharField(max_length=120, null=True, blank=True)
    file            = models.FileField(
                        upload_to=upload_product_file_loc, 
                        storage=ProtectedS3Storage(), #FileSystemStorage(location=settings.PROTECTED_ROOT)
                        ) # path
    #filepath        = models.TextField() # '/protected/path/to/the/file/myfile.mp3'
    free            = models.BooleanField(default=False) # purchase required
    user_required   = models.BooleanField(default=False) # user doesn't matter


    def __str__(self):
        return str(self.file.name)

    @property
    def display_name(self):
        og_name = get_filename(self.file.name)
        if self.name:
            return self.name
        return og_name

    def get_default_url(self):
        return self.product.get_absolute_url()

    def generate_download_url(self):
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'S3DIRECT_REGION')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        if not secret_key or not access_key or not bucket or not region:
            return "/product-not-found/"
        PROTECTED_DIR_NAME = getattr(settings, 'PROTECTED_DIR_NAME', 'protected')
        path = "{base}/{file_path}".format(base=PROTECTED_DIR_NAME, file_path=str(self.file))
        aws_dl_object =  AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(path, new_filename=self.display_name)
        return file_url

    def get_download_url(self): # detail view
        return reverse("products:download", 
                    kwargs={"slug": self.product.slug, "pk": self.pk}
                )

from django.urls import path # used for routing URLs to the appropriate view functions within a Django application using the URL dispatcher
from . import views # Import views

# All the URL patterns for routing
urlpatterns = [
    path('',views.index, name='index'), # The home page would render the 'index' view
    path('video_feed/', views.video_feed, name='video_feed'), # /video_feed/ route would render the 'video_feed' view
    path('meditate/',views.meditate, name='meditate'), #  /meditate/ route would render the 'meditate' view
    path('pred_health/', views.predict_emotions, name='health_pred'), # /pred_health/ route would render the 'predict_emotions' view
]
from django.urls import path

from .views import CreatePromptView, SimilarPromptsView

urlpatterns = [
    path("prompts", CreatePromptView.as_view(), name="create-prompt"),
    path("prompts/similar", SimilarPromptsView.as_view(), name="similar-prompts"),
]

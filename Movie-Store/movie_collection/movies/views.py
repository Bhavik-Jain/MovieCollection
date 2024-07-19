from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie, Collection
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from configurations.utils import success_response, error_response,fetch_movies_with_retries
from configurations.message import *
import requests
from configurations import config
from django.http import Http404
from collections import Counter


class MovieView(APIView):
    """
        Description: API to fetch all movies from third party api

        POST /movies/movies/
        Responses:
            200: Movies Fetched
            500: Server error
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            url = config.THIRD_PARTY_API
            movies = fetch_movies_with_retries(url)
            
            if movies:
                data = {
                    "count": movies['count'],
                    "next": movies['next'],
                    "previous": movies['previous'],
                    "data": movies['results']
                }
                return success_response(data=data, message=MOVIES_FETCHED, status=status.HTTP_200_OK)
        except Exception as error:
            return error_response(api='MovieView', message=FETCH_MOVIES_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CollectionsView(APIView):
    """
        Description: API to get & create collections for user

        GET /movies/collection/
        POST /movies/collection/
        Responses:
            200: Collections fetched
            201: Collection Created
            500: Server error
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        collections = Collection.objects.filter(user=request.user).prefetch_related('movies')
        serializer = CollectionSerializer(collections, many=True)
        # Flatten the list of genres from all movies in collections

        all_genres = [genre for collection in collections for movie in collection.movies.all() for genre in movie.genres.split(', ')]
        
        # Count occurrences of each genre
        genre_counts = Counter(all_genres)
        
        # Get the top 3 genres
        top_genres = ', '.join([genre for genre, _ in genre_counts.most_common(3)])
        
        data = {
            "is_success": True,
            "data": {
                "collections": serializer.data,
                "favourite_genres": top_genres
            }
        }
        return success_response(message=COLLECTION_RETRIEVED, status=status.HTTP_200_OK, data=data)

    def post(self, request):
        try:
            data = request.data
            print(data, "dataaaaaaaaaaaa")
            data['user'] = request.user.id  # Set the user field
            serializer = CollectionSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                collection = serializer.save()
                return success_response(data={'collection_uuid': collection.uuid}, message=COLLECTION_CREATED, status=status.HTTP_201_CREATED)
            return error_response(api='CollectionView-Post', message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as error:
            print("error ---->", error)
            return error_response(api='CollectionView-Post', message=str(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CollectionDetailView(APIView):
    """
        Description: CRUD APIs for Collections

        GET /movies/collection/<uuid>/
        PUT /movies/collection/<uuid>/
        DELETE /movies/collection/<uuid>/
        Responses:
            200: Collections fetched
            500: Server error
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, uuid):
        try:
            return Collection.objects.get(uuid=uuid, user=self.request.user)
        except Collection.DoesNotExist:
            raise Http404

    def get(self, request, uuid):
        collection = self.get_object(uuid)
        serializer = CollectionSerializer(collection)
        return success_response(status=status.HTTP_200_OK, data=serializer.data, message=COLLECTION_RETRIEVED)

    def put(self, request, uuid):
        collection = self.get_object(uuid)
        data = request.data

        serializer = CollectionSerializer(collection, data=data, partial=True)
        if serializer.is_valid():
            collection = serializer.save()
            return success_response(status=status.HTTP_200_OK, data=serializer.data, message=COLLECTION_UPDATED)
        return error_response(api='collection_update', message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):
        try:
            collection = self.get_object(uuid)
            collection.delete()
            return success_response(message=COLLECTION_DELETED, status=status.HTTP_200_OK)
        except Exception as error:
            print("error --->", error)
            return error_response(api='CollectionDetailView-DELETE', message=str(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


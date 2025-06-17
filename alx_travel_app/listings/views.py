from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listings.
    
    Provides CRUD operations for property listings.
    - GET /api/listings/ - List all listings
    - POST /api/listings/ - Create a new listing
    - GET /api/listings/{id}/ - Retrieve a specific listing
    - PUT /api/listings/{id}/ - Update a listing
    - DELETE /api/listings/{id}/ - Delete a listing
    - GET /api/listings/available/ - List only available listings
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'city', 'state', 'country', 'is_available', 'host']
    search_fields = ['title', 'description', 'address', 'city', 'state', 'country']
    ordering_fields = ['price_per_night', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
    def perform_update(self, serializer):
        # Only allow the host to update their own listing
        if serializer.instance.host != self.request.user:
            raise permissions.PermissionDenied("You can only update your own listings.")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow the host to delete their own listing
        if instance.host != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own listings.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """List only available listings."""
        available_listings = self.queryset.filter(is_available=True)
        serializer = self.get_serializer(available_listings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """List current user's listings."""
        if not request.user.is_authenticated:
            raise permissions.PermissionDenied("Authentication required.")
        user_listings = self.queryset.filter(host=request.user)
        serializer = self.get_serializer(user_listings, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    Provides CRUD operations for property bookings.
    - GET /api/bookings/ - List all bookings
    - POST /api/bookings/ - Create a new booking
    - GET /api/bookings/{id}/ - Retrieve a specific booking
    - PUT /api/bookings/{id}/ - Update a booking
    - DELETE /api/bookings/{id}/ - Delete a booking
    - GET /api/bookings/my_bookings/ - List current user's bookings
    - GET /api/bookings/listing/{listing_id}/ - List bookings for a specific listing
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'listing', 'guest']
    ordering_fields = ['check_in_date', 'check_out_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        # Regular users can only see their own bookings
        return Booking.objects.filter(guest=user)
    
    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)
    
    def perform_update(self, serializer):
        # Only allow the guest or listing host to update the booking
        booking = serializer.instance
        user = self.request.user
        if booking.guest != user and booking.listing.host != user:
            raise permissions.PermissionDenied("You can only update your own bookings or bookings for your listings.")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow the guest or listing host to delete the booking
        user = self.request.user
        if instance.guest != user and instance.listing.host != user:
            raise permissions.PermissionDenied("You can only delete your own bookings or bookings for your listings.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """List current user's bookings."""
        user_bookings = self.queryset.filter(guest=request.user)
        serializer = self.get_serializer(user_bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def listing_bookings(self, request, listing_id=None):
        """List bookings for a specific listing."""
        if listing_id:
            try:
                listing = Listing.objects.get(id=listing_id)
                # Only allow listing host to see bookings for their listing
                if listing.host != request.user:
                    raise permissions.PermissionDenied("You can only view bookings for your own listings.")
                listing_bookings = self.queryset.filter(listing=listing)
                serializer = self.get_serializer(listing_bookings, many=True)
                return Response(serializer.data)
            except Listing.DoesNotExist:
                return Response({"error": "Listing not found."}, status=404)
        return Response({"error": "Listing ID required."}, status=400)

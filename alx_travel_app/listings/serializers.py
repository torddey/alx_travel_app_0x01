from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'address', 'city', 'state', 
            'country', 'zip_code', 'price_per_night', 'property_type',
            'bedrooms', 'bathrooms', 'max_guests', 'amenities', 'images',
            'is_available', 'host', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['host'] = self.context['request'].user
        return super().create(validated_data)

class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    guest = UserSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'check_in_date',
            'check_out_date', 'number_of_guests', 'total_price', 'status',
            'special_requests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'guest', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['guest'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        # Check if check_out_date is after check_in_date
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        
        # Check if the listing exists and is available
        try:
            listing = Listing.objects.get(id=data['listing_id'])
            if not listing.is_available:
                raise serializers.ValidationError("This listing is not available for booking.")
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing not found.")
        
        # Check if number of guests doesn't exceed max_guests
        if data['number_of_guests'] > listing.max_guests:
            raise serializers.ValidationError(f"Number of guests cannot exceed {listing.max_guests}.")
        
        return data 
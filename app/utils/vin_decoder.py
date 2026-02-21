import requests
from flask import current_app


class VINDecoder:
    """Decode VIN using NHTSA API"""
    
    NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{}?format=json"
    
    @classmethod
    def decode(cls, vin):
        """Decode VIN and return vehicle information"""
        if not vin or len(vin) != 17:
            return {'error': 'Invalid VIN. Must be 17 characters'}
        
        try:
            response = requests.get(cls.NHTSA_API_URL.format(vin), timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Results' not in data:
                return {'error': 'Unable to decode VIN'}
            
            results = {item['Variable']: item['Value'] for item in data['Results']}
            
            return {
                'vin': vin,
                'make': results.get('Make', ''),
                'model': results.get('Model', ''),
                'year': results.get('Model Year', ''),
                'body_class': results.get('Body Class', ''),
                'engine': results.get('Engine Model', ''),
                'displacement': results.get('Displacement (L)', ''),
                'cylinders': results.get('Engine Number of Cylinders', ''),
                'fuel_type': results.get('Fuel Type - Primary', ''),
                'transmission': results.get('Transmission Style', ''),
                'drive_type': results.get('Drive Type', ''),
                'vehicle_type': results.get('Vehicle Type', ''),
                'manufacturer': results.get('Manufacturer Name', ''),
                'plant_city': results.get('Plant City', ''),
                'plant_country': results.get('Plant Country', ''),
                'error_code': results.get('Error Code', '0')
            }
        
        except requests.RequestException as e:
            current_app.logger.error(f"VIN decode error: {str(e)}")
            return {'error': f'VIN decode failed: {str(e)}'}
        except Exception as e:
            current_app.logger.error(f"Unexpected VIN decode error: {str(e)}")
            return {'error': 'Unexpected error during VIN decode'}
    
    @classmethod
    def validate_vin(cls, vin):
        """Validate VIN format"""
        if not vin:
            return False
        
        # Basic validation
        if len(vin) != 17:
            return False
        
        # VIN cannot contain I, O, or Q
        invalid_chars = set('IOQ')
        if any(char in invalid_chars for char in vin.upper()):
            return False
        
        return True

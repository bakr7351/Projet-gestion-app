"""
API Calculation Resources
REST API endpoints for absorption and desorption calculations
"""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
import uuid
from datetime import datetime

from backend.services.absorption_calculator import AbsorptionCalculator
from backend.middlewares.rate_limiter import require_rate_limit
from backend.middlewares.security_middleware import require_input_validation

class AbsorptionCalculationSchema(Schema):
    """Schema for absorption calculation parameters"""
    G_prime = fields.Float(required=True, validate=lambda x: x > 0)
    L_prime = fields.Float(required=True, validate=lambda x: x > 0)
    m = fields.Float(required=True, validate=lambda x: x > 0)
    y0 = fields.Float(required=True, validate=lambda x: 0 <= x <= 1)
    y_obj = fields.Float(required=True, validate=lambda x: 0 <= x <= 1)
    N = fields.Int(load_default=10, validate=lambda x: 1 <= x <= 100)

class DesorptionCalculationSchema(Schema):
    """Schema for desorption calculation parameters"""
    G = fields.Float(required=True, validate=lambda x: x > 0)
    L = fields.Float(required=True, validate=lambda x: x > 0)
    m = fields.Float(required=True, validate=lambda x: x > 0)
    x0 = fields.Float(required=True, validate=lambda x: 0 <= x <= 1)
    x_obj = fields.Float(required=True, validate=lambda x: 0 <= x <= 1)
    N = fields.Int(load_default=10, validate=lambda x: 1 <= x <= 100)

class CalculationResource(Resource):
    """Resource for individual calculations"""
    
    @require_rate_limit('calculations')
    @require_input_validation()
    def post(self, calc_type):
        """
        Perform calculation (absorption or desorption)
        ---
        tags:
          - Calculations
        parameters:
          - in: path
            name: calc_type
            type: string
            enum: [absorption, desorption]
            required: true
          - in: body
            name: parameters
            schema:
              type: object
              properties:
                G_prime:
                  type: number
                  description: Gas flow rate (for absorption)
                L_prime:
                  type: number
                  description: Liquid flow rate (for absorption)
                G:
                  type: number
                  description: Gas flow rate (for desorption)
                L:
                  type: number
                  description: Liquid flow rate (for desorption)
                m:
                  type: number
                  description: Mass transfer coefficient
                y0:
                  type: number
                  description: Initial gas concentration (absorption)
                y_obj:
                  type: number
                  description: Target gas concentration (absorption)
                x0:
                  type: number
                  description: Initial liquid concentration (desorption)
                x_obj:
                  type: number
                  description: Target liquid concentration (desorption)
                N:
                  type: integer
                  description: Number of stages
                  default: 10
        responses:
          200:
            description: Calculation completed successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                calculation_id:
                  type: string
                results:
                  type: object
                metadata:
                  type: object
          400:
            description: Invalid parameters
          404:
            description: Invalid calculation type
        """
        if calc_type not in ['absorption', 'desorption']:
            return {
                'success': False,
                'error': {
                    'code': 'INVALID_CALCULATION_TYPE',
                    'message': f'Invalid calculation type: {calc_type}'
                }
            }, 404
        
        # Select appropriate schema
        schema = AbsorptionCalculationSchema() if calc_type == 'absorption' else DesorptionCalculationSchema()
        
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as err:
            return {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid calculation parameters',
                    'details': err.messages
                }
            }, 400
        
        # Get user ID if authenticated (optional for API)
        user_id = None
        try:
            user_id_str = get_jwt_identity()
            if user_id_str:
                user_id = int(user_id_str)  # Convert to int
        except:
            pass  # Anonymous access allowed
        
        # Perform calculation
        calculator = AbsorptionCalculator()
        calculation_id = str(uuid.uuid4())
        
        try:
            if calc_type == 'absorption':
                results = calculator.calculate_absorption(
                    G_prime=data['G_prime'],
                    L_prime=data['L_prime'],
                    m=data['m'],
                    y0=data['y0'],
                    y_obj=data['y_obj'],
                    N=data['N']
                )
            else:  # desorption
                results = calculator.calculate_desorption(
                    G=data['G'],
                    L=data['L'],
                    m=data['m'],
                    x0=data['x0'],
                    x_obj=data['x_obj'],
                    N=data['N']
                )
            
            # Add metadata
            metadata = {
                'calculation_id': calculation_id,
                'calculation_type': calc_type,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'parameters': data
            }
            
            return {
                'success': True,
                'calculation_id': calculation_id,
                'data': {
                    'calculation_results': results['calculation_results'],
                    'mccabe_thiele_graph': results.get('mccabe_thiele_graph'),
                    'surface_3d_graph': results.get('surface_3d_graph'),
                    'performance': results['performance']
                },
                'metadata': metadata
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'code': 'CALCULATION_ERROR',
                    'message': f'Calculation failed: {str(e)}'
                }
            }, 500

class BatchCalculationResource(Resource):
    """Resource for batch calculations"""
    
    @jwt_required()
    def post(self):
        """
        Submit batch calculation job
        ---
        tags:
          - Calculations
        security:
          - JWT: []
        consumes:
          - multipart/form-data
        parameters:
          - in: formData
            name: file
            type: file
            required: true
            description: CSV file with calculation parameters
          - in: formData
            name: calculation_type
            type: string
            enum: [absorption, desorption]
            required: true
        responses:
          202:
            description: Batch job submitted successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                job_id:
                  type: string
                status:
                  type: string
          400:
            description: Invalid file or parameters
          401:
            description: Authentication required
        """
        user_id = int(get_jwt_identity())  # Convert to int
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return {
                'success': False,
                'error': {
                    'code': 'NO_FILE',
                    'message': 'No file uploaded'
                }
            }, 400
        
        file = request.files['file']
        calc_type = request.form.get('calculation_type')
        
        if not file.filename:
            return {
                'success': False,
                'error': {
                    'code': 'EMPTY_FILE',
                    'message': 'No file selected'
                }
            }, 400
        
        if calc_type not in ['absorption', 'desorption']:
            return {
                'success': False,
                'error': {
                    'code': 'INVALID_CALCULATION_TYPE',
                    'message': 'calculation_type must be absorption or desorption'
                }
            }, 400
        
        # TODO: Implement batch processing with Celery
        # For now, return a placeholder response
        job_id = str(uuid.uuid4())
        
        return {
            'success': True,
            'job_id': job_id,
            'status': 'queued',
            'message': 'Batch processing will be implemented in Phase 2'
        }, 202
    
    @jwt_required()
    def get(self):
        """
        Get batch job status and results
        ---
        tags:
          - Calculations
        security:
          - JWT: []
        parameters:
          - in: query
            name: job_id
            type: string
            required: true
        responses:
          200:
            description: Job status retrieved successfully
          400:
            description: Missing job_id parameter
          404:
            description: Job not found
        """
        job_id = request.args.get('job_id')
        
        if not job_id:
            return {
                'success': False,
                'error': {
                    'code': 'MISSING_JOB_ID',
                    'message': 'job_id parameter is required'
                }
            }, 400
        
        # TODO: Implement job status retrieval
        return {
            'success': True,
            'job_id': job_id,
            'status': 'pending',
            'message': 'Batch processing will be implemented in Phase 2'
        }, 200
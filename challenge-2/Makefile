
.DELETE_ON_ERROR:
all: raw-data preprocess webservice

PYTHON_VERSION := $(shell cat infrastructure/config.yml | yq -r .python_version)
LAMBDA_RUNTIME := python${PYTHON_VERSION}
LAMBDA_LAYER := $(shell cat infrastructure/config.yml | yq -r .lambda_layer_name)
NUMPY_LAYER_ARN := "arn:aws:lambda:eu-central-1:292169987271:layer:AWSLambda-Python37-SciPy1x:35"
ETL_LAMBDA_NAME := $(shell cat infrastructure/config.yml | yq -r .etl_lambda_name)
RAWDATA_BUCKET := $(shell cat infrastructure/config.yml | yq -r .rawdata_bucket)
DEST_TABLE := $(shell cat infrastructure/config.yml | yq -r .well_imagers_table)
IMAGE_SIZE := $(shell cat infrastructure/config.yml | yq -r .images_size)
TEST_DATA_FILE := $(shell cat infrastructure/config.yml | yq -r .test_data_file)

# init local build environment
init: requirements.txt
	pip3 install -r requirements.txt
	ls ~/.aws || aws configure

build/layer-package.zip: PKG_DIR = "build/python"
build/layer-package.zip: infrastructure/requirements.etl.txt
	rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}
	rm -f build/layer-package.zip
	docker run --rm -v $$(pwd):/foo -w /foo lambci/lambda:build-python$(PYTHON_VERSION) \
		pip install -r infrastructure/requirements.etl.txt --no-deps -t ${PKG_DIR}
	cd build && zip -r layer-package.zip python
	rm -rf ${PKG_DIR}

# build layer of 3d party library dependencies for ETL lambda
build/lambda-layer: build/layer-package.zip
	aws lambda publish-layer-version --layer-name $(LAMBDA_LAYER) \
	--zip-file fileb://build/layer-package.zip \
	--description "Layer with pandas 1.2.0 build for Python 3.7. Requires numpy layer" --license-info "MIT" \
	--compatible-runtimes $(LAMBDA_RUNTIME) > build/lambda-layer

build/lambda-package.zip: $(shell find src -type f -name "*.py")
	rm -f build/lambda-package.zip
	cd src && zip -r ../build/lambda-package.zip .
	cd ../common/src && zip -g -r ../../challenge-2/build/lambda-package.zip .

# The following targets are created during Ansible infrastructure provision

build/iam-role:
	ansible-playbook infrastructure/infrastructure-play.yml

build/ec2:
	ansible-playbook infrastructure/infrastructure-play.yml

build/rawdata-bucket:
	ansible-playbook infrastructure/infrastructure-play.yml

# build ETL lambda function
build/etl-lambda: build/lambda-package.zip build/lambda-layer build/iam-role
	-aws lambda delete-function --function-name $(ETL_LAMBDA_NAME)
	aws lambda create-function --function-name $(ETL_LAMBDA_NAME) \
	--zip-file fileb://build/lambda-package.zip --handler etl_handler.lambda_handler --runtime $(LAMBDA_RUNTIME) \
	--role $$(cat build/iam-role | yq -r "first(..|.arn?)") \
	--layers $(NUMPY_LAYER_ARN) $$(cat build/lambda-layer | yq -r .LayerVersionArn) > build/etl-lambda \
	--environment '{"Variables": {"DEST_TABLE": "$(DEST_TABLE)", "IMAGE_SIZE": "$(IMAGE_SIZE)"}}' \
	--timeout 900 \
	--memory-size 1024

# upload test example data to S3 storage
raw-data: build/rawdata-bucket
	aws s3 cp $(TEST_DATA_FILE) s3://$(RAWDATA_BUCKET)/test-well

# run ETL job synchronosly on test example data
preprocess: build/etl-lambda build/rawdata-bucket
	aws lambda invoke --function-name $(ETL_LAMBDA_NAME) --payload '{ "bucket": "$(RAWDATA_BUCKET)", "key": "test-well"}' build/preprocess.json

# provision web service and print help information about it
webservice: build/ec2
	@echo "Test data is preprocessed. Web API service is running. \n\n"
	@echo The service is running at: $$(cat build/ec2 | yq -r '.instances | .[0].public_dns_name')":8080/plants?year=2018&state=AL&top_n=4\n"
	@echo API documentation: $$(cat build/ec2 | yq -r '.instances | .[0].public_dns_name')":8080/docs\n"
	@echo Example call: $$(cat build/ec2 | yq -r '.instances | .[0].public_dns_name')":8080/imagers/test-well?min_depth=9000.1&max_depth=9000.3&colormap=gist_earth\n"
	@echo "If colormap is not present the result data is a 2d (height, width) array."
	@echo "If it was provided, the data is a 3d (height, width, channel) array"
	@echo "colormap name - is a colormap function name from matplotlib.cm package"

# removes all build artifacts
.PHONY: clean
clean:
	-aws lambda delete-function --function-name $(ETL_LAMBDA_NAME)
	-aws lambda delete-layer-version --layer-name $$(cat build/lambda-layer | yq -r .LayerArn) \
	--version-number $$(cat build/lambda-layer | yq -r .Version)
	ansible-playbook infrastructure/cleanup-play.yml

# adds random prefix to the names of created AWS resources
# this is required in a development iteration to avoid some AWS eventual consistency problems 
# if you want to rebuild the infrastructure it's better to run:
# make clean && make salt && make
.PHONY: salt
salt: SALT := $(shell echo $$RANDOM)
salt:
	cat infrastructure/config.yml | yq -y '. + { \
	 iam_role_name: (.iam_role_name + "--$(SALT)"), \
	 etl_lambda_name: (.etl_lambda_name + "--$(SALT)"), \
	 well_imagers_table: (.well_imagers_table + "--$(SALT)"), \
	 sg_name: (.sg_name + "--$(SALT)"), \
	 iam_policy_name: (.iam_policy_name + "--$(SALT)"), \
	}' > infrastructure/config.yml.tmp
	mv infrastructure/config.yml.tmp infrastructure/config.yml

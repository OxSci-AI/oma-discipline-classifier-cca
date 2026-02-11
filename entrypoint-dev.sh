#!/bin/bash

# CodeArtifact Configuration Script
# Used to configure Poetry to use AWS CodeArtifact private repository
# Packages are deployed to AWS CodeArtifact private repository, requires AWS credentials configuration and AWS_PROFILE environment variable, recommended to use SSO login
#  1. Install AWS CLI
#  2. Ask admin to provision AWS account
#  3. Run `aws configure sso --profile oxsci-dev` to configure AWS credentials, enter the following configuration:
#     - SSO session name (Recommended): oxsci-dev
#     - SSO start URL: https://oxsci-ai.awsapps.com/start
#     - SSO region: ap-southeast-1
#     - SSO registration scopes: sso:account:access
#  4. A login page will pop up for authentication
#  5. After successful login, select default region as ap-southeast-1, and default output as json
#  6. Copy this script to the project root directory, and run `chmod +x entrypoint-dev.sh`
#  7. Run `./entrypoint-dev.sh` in the project root directory (needs to be executed every 12 hours)

set -e # Exit immediately on error

PROFILE="oxsci-dev"
DOMAIN="oxsci-domain"
DOMAIN_OWNER="000373574646"
REPOSITORY="oxsci-pypi"
REGION="ap-southeast-1"

echo "🔧 Starting AWS CodeArtifact configuration for Poetry..."

# Check if AWS CLI is installed
if ! command -v aws &>/dev/null; then
    echo "❌ AWS CLI not installed, please install AWS CLI first"
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &>/dev/null; then
    echo "❌ Poetry not installed, please install Poetry first"
    exit 1
fi

# Check if AWS Profile exists
echo "🔍 Checking AWS Profile: $PROFILE"
if ! aws configure list-profiles | grep -q "^$PROFILE$"; then
    echo "❌ AWS Profile '$PROFILE' does not exist"
    echo ""
    echo "Please configure AWS Profile, recommended using SSO:"
    echo "  aws configure sso --profile $PROFILE"
    echo ""
    echo "Or configure using traditional method:"
    echo "  aws configure --profile $PROFILE"
    echo ""
    echo "Ensure Profile has CodeArtifact related permissions:"
    echo "  - codeartifact:GetRepositoryEndpoint"
    echo "  - codeartifact:GetAuthorizationToken"
    exit 1
fi

# Test if Profile is valid, if not, try automatic login
echo "🔐 Verifying AWS Profile permissions..."
if ! aws sts get-caller-identity --profile $PROFILE >/dev/null 2>&1; then
    echo "⚠️  AWS Profile '$PROFILE' cannot verify identity, attempting automatic login..."
    if aws sso login --profile $PROFILE; then
        echo "✅ SSO login successful"
    else
        echo "❌ SSO login failed, please run manually:"
        echo "  aws sso login --profile $PROFILE"
        exit 1
    fi
else
    echo "✅ AWS Profile verification successful"
fi

# Get CodeArtifact repository URL
echo "🌐 Getting CodeArtifact repository endpoint..."
REPO_URL=$(aws codeartifact get-repository-endpoint \
    --profile $PROFILE \
    --domain $DOMAIN \
    --domain-owner $DOMAIN_OWNER \
    --repository $REPOSITORY \
    --format pypi \
    --region $REGION \
    --query repositoryEndpoint --output text)

if [ $? -ne 0 ] || [ -z "$REPO_URL" ]; then
    echo "❌ Failed to get repository endpoint, please check permissions and parameters"
    exit 1
fi

echo "✅ Repository endpoint retrieved successfully: $REPO_URL"

# Configure Poetry repository
echo "📦 Configuring Poetry repository..."
poetry config repositories.oxsci-ca ${REPO_URL}

if [ $? -ne 0 ]; then
    echo "❌ Poetry repository configuration failed"
    exit 1
fi

echo "✅ Poetry repository configured successfully"

# Get authentication token
echo "🔑 Getting authentication token..."
AUTH_TOKEN=$(aws codeartifact get-authorization-token \
    --profile $PROFILE \
    --domain $DOMAIN \
    --domain-owner $DOMAIN_OWNER \
    --region $REGION \
    --query authorizationToken \
    --output text)

if [ $? -ne 0 ] || [ -z "$AUTH_TOKEN" ]; then
    echo "❌ Failed to get authentication token"
    exit 1
fi

echo "✅ Authentication token retrieved successfully"

# Configure Poetry authentication
echo "🔐 Configuring Poetry authentication..."
poetry config http-basic.oxsci-ca aws ${AUTH_TOKEN}

if [ $? -ne 0 ]; then
    echo "❌ Poetry authentication configuration failed"
    exit 1
fi

echo "✅ Poetry authentication configured successfully"

echo ""
echo "🎉 CodeArtifact configuration complete!"
echo "📋 Configuration info:"
echo "  - Repository name: oxsci-ca"
echo "  - Repository URL: $REPO_URL"
echo "  - Profile: $PROFILE"
echo "  - Token validity: 12 hours"
echo ""
echo "You can now install dependencies with:"
echo "  poetry install"
echo ""
echo "💡 Tip: Token expires after 12 hours, please re-run this script"

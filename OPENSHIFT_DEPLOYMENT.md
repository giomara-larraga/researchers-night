# OpenShift Deployment Guide

This guide explains how to deploy the Phone Selector Dash application to OpenShift.

## Prerequisites

1. **OpenShift CLI (oc)** installed and configured
   - Download from: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html
2. **Access to an OpenShift cluster**
   - Login credentials or service account token
3. **Git repository** with your code (already set up)

## Quick Start

### Option 1: Automated Deployment (Recommended)

**Windows:**

```cmd
# Deploy the application
deploy-openshift.bat deploy

# Check status
deploy-openshift.bat status

# View logs
deploy-openshift.bat logs

# Get application URL
deploy-openshift.bat url
```

**Linux/Mac:**

```bash
# Make script executable
chmod +x deploy-openshift.sh

# Deploy the application
./deploy-openshift.sh deploy

# Check status
./deploy-openshift.sh status

# View logs
./deploy-openshift.sh logs
```

### Option 2: Manual Deployment

1. **Login to OpenShift:**

```bash
oc login <your-openshift-cluster-url>
```

2. **Create/Switch to Project:**

```bash
oc new-project phone-selector --display-name="Phone Selector App"
# OR if project exists:
oc project phone-selector
```

3. **Deploy using Template:**

```bash
oc process -f openshift/template.yaml \
  -p APP_NAME=phone-selector \
  -p GIT_REPO=https://github.com/giomara-larraga/researchers-night.git \
  -p MEMORY_LIMIT=512Mi \
  -p CPU_LIMIT=500m | oc apply -f -
```

4. **Monitor Build:**

```bash
oc logs -f bc/phone-selector
```

5. **Check Deployment Status:**

```bash
oc get pods
oc get routes
```

### Option 3: OpenShift Web Console UI Deployment 🖥️

You can deploy your Phone Selector app directly from the OpenShift web console using several methods:

#### Method 1: Using the Developer Catalog (Easiest)

1. **Access OpenShift Web Console:**

   - Open your OpenShift cluster URL in a web browser
   - Login with your credentials

2. **Create or Select Project:**

   - Click **"Projects"** → **"Create Project"**
   - Name: `phone-selector`
   - Display name: `Phone Selector App`
   - Description: `Multi-criteria phone selection application`

3. **Deploy Using Template:**
   - Go to **"Developer"** perspective (top-left dropdown)
   - Click **"+Add"** → **"From Catalog"**
   - Search for **"Import from Git"** or click **"Git Repository"**
4. **Configure Git Repository:**

   - **Git Repo URL:** `https://github.com/giomara-larraga/researchers-night.git`
   - **Git Reference:** `master` (or your branch)
   - **Context Dir:** Leave empty (uses root directory)

5. **Configure Build:**

   - **Builder Image:** Select **"Python"** (should auto-detect)
   - **Builder Image Version:** `3.10-ubi8` or latest
   - **Application Name:** `phone-selector`
   - **Name:** `phone-selector`

6. **Advanced Options:**
   - Click **"Show advanced Git options"**
   - **Dockerfile Path:** `Dockerfile` (if using Docker strategy)
7. **Resource Configuration:**

   - **CPU Request:** `250m`
   - **CPU Limit:** `500m`
   - **Memory Request:** `256Mi`
   - **Memory Limit:** `512Mi`

8. **Environment Variables:**

   - Add environment variables:
     - `PORT` = `8050`
     - `DEBUG` = `false`

9. **Create Route:**

   - Check **"Create a route to the application"**
   - **Hostname:** Leave empty for auto-generation
   - **Path:** `/`
   - **Target Port:** `8050`
   - **Secure Route:** Check this for HTTPS

10. **Deploy:**
    - Click **"Create"**
    - Monitor the build progress in the **"Builds"** section

#### Method 2: Import YAML/Template via UI

1. **Navigate to Import YAML:**

   - Go to **"Administrator"** perspective
   - Click **"+"** (Import YAML) in the top navigation

2. **Upload Template:**

   - Copy the contents of `openshift/template.yaml`
   - Paste into the YAML editor
   - Click **"Create"**

3. **Process Template:**
   - Go to **"Developer"** → **"+Add"** → **"From Catalog"**
   - Search for **"Phone Selector App"** template
   - Click on it and fill in parameters:
     - **Application Name:** `phone-selector`
     - **Git Repository URL:** `https://github.com/giomara-larraga/researchers-night.git`
     - **Git Reference:** `master`
     - **Memory Limit:** `512Mi`
     - **CPU Limit:** `500m`
   - Click **"Create"**

#### Method 3: Drag & Drop Individual YAML Files

1. **Navigate to Import:**

   - **"Administrator"** perspective → **"+"** (Import YAML)

2. **Import Files in Order:**

   - Upload each file from the `openshift/` directory:
     - `imagestream.yaml`
     - `buildconfig.yaml`
     - `configmap.yaml`
     - `deployment.yaml`
     - `service.yaml`
     - `route.yaml`

3. **Start Build:**
   - Go to **"Builds"** → **"Build Configs"**
   - Click on your build config
   - Click **"Start Build"**

#### Method 4: Using Source-to-Image (S2I) Wizard

1. **Start S2I Process:**

   - **"Developer"** perspective → **"+Add"** → **"Import from Git"**

2. **Configure Source:**

   - **Git Repo URL:** `https://github.com/giomara-larraga/researchers-night.git`
   - **Show Advanced Git Options:**
     - **Git Reference:** `master`
     - **Context Dir:** `/` (root)

3. **Select Builder:**

   - **Builder Image:** Python
   - **Builder Image Version:** 3.10

4. **Application Configuration:**

   - **Application:** Create new application `phone-selector-app`
   - **Name:** `phone-selector`
   - **Resources:** Deployment

5. **Advanced Options:**
   - **Create a route:** ✓ Checked
   - **Labels:** Add `app=phone-selector`
6. **Environment Variables:**

   - Click **"Deployment"** → Add Environment Variables:
     - `PORT` = `8050`
     - `DEBUG` = `false`
     - `PYTHONUNBUFFERED` = `1`

7. **Create Application:**
   - Click **"Create"**

### 🖥️ **Monitoring Deployment in Web Console**

After deployment, you can monitor your application:

1. **Overview Dashboard:**

   - **"Developer"** → **"Topology"**
   - See visual representation of your app components

2. **Build Monitoring:**

   - **"Builds"** → **"Build Configs"** → Click your build
   - View build logs in real-time

3. **Pod Monitoring:**

   - **"Workloads"** → **"Pods"**
   - Click on pod to see logs, terminal, events

4. **Route Access:**

   - **"Networking"** → **"Routes"**
   - Click on route URL to access your application

5. **Metrics & Monitoring:**
   - **"Monitoring"** → **"Metrics"**
   - View CPU, memory, and network usage

### 🎯 **UI Deployment Advantages:**

- ✅ **Visual Interface** - Easy point-and-click deployment
- ✅ **Real-time Monitoring** - Watch builds and deployments live
- ✅ **Integrated Logs** - View logs directly in browser
- ✅ **Resource Management** - Easy scaling and configuration
- ✅ **No CLI Required** - Perfect for users who prefer GUI
- ✅ **Template Integration** - Use custom templates seamlessly

### 🔧 **Post-Deployment via UI:**

After successful deployment:

1. **Get Application URL:** **"Networking"** → **"Routes"** → Copy URL
2. **Scale Application:** **"Workloads"** → **"Deployments"** → Adjust replica count
3. **View Logs:** **"Workloads"** → **"Pods"** → Select pod → **"Logs"** tab
4. **Access Terminal:** **"Workloads"** → **"Pods"** → Select pod → **"Terminal"** tab

## Deployment Files Overview

### Core OpenShift Resources

- **`openshift/deployment.yaml`** - Kubernetes Deployment configuration
- **`openshift/service.yaml`** - Service to expose the application
- **`openshift/route.yaml`** - OpenShift Route for external access
- **`openshift/buildconfig.yaml`** - Build configuration for source-to-image
- **`openshift/imagestream.yaml`** - Image stream for container images
- **`openshift/configmap.yaml`** - Configuration data
- **`openshift/template.yaml`** - Complete template for easy deployment

### Deployment Scripts

- **`deploy-openshift.sh`** - Linux/Mac deployment script
- **`deploy-openshift.bat`** - Windows deployment script

## Configuration Options

### Environment Variables

- `PORT` - Application port (default: 8050)
- `DEBUG` - Enable debug mode (default: false)
- `WORKERS` - Number of Gunicorn workers (default: 1)
- `TIMEOUT` - Request timeout in seconds (default: 120)

### Resource Limits

Default resource allocation:

- **CPU**: 250m requests, 500m limits
- **Memory**: 256Mi requests, 512Mi limits

To modify resources, edit the template parameters:

```bash
oc process -f openshift/template.yaml \
  -p MEMORY_LIMIT=1Gi \
  -p CPU_LIMIT=1000m | oc apply -f -
```

## Monitoring and Troubleshooting

### Check Application Status

```bash
# View all resources
oc get all -l app=phone-selector

# Check pod status
oc get pods -l app=phone-selector

# View events
oc get events --sort-by=.metadata.creationTimestamp
```

### View Logs

```bash
# Application logs
oc logs -f deployment/phone-selector

# Build logs
oc logs -f bc/phone-selector

# All pods logs
oc logs -l app=phone-selector --all-containers=true
```

### Debug Issues

```bash
# Describe pod for detailed info
oc describe pod <pod-name>

# Get into running container
oc rsh deployment/phone-selector

# Port forward for local testing
oc port-forward service/phone-selector-service 8050:8050
```

## Scaling

### Manual Scaling

```bash
# Scale to 3 replicas
oc scale deployment phone-selector --replicas=3

# Auto-scale based on CPU usage
oc autoscale deployment phone-selector --min=1 --max=5 --cpu-percent=80
```

## Updates and Rollbacks

### Trigger New Build

```bash
# Start new build from latest source code
oc start-build phone-selector

# Build from specific Git reference
oc start-build phone-selector --commit=<git-commit-hash>
```

### Rolling Updates

```bash
# Update image
oc set image deployment/phone-selector phone-selector=phone-selector:new-tag

# Check rollout status
oc rollout status deployment/phone-selector

# Rollback to previous version
oc rollout undo deployment/phone-selector
```

## Security Considerations

The deployment includes several security best practices:

- **Non-root user**: Application runs as user ID 1001
- **Read-only root filesystem**: Where possible
- **Security context**: Drops all capabilities
- **Resource limits**: Prevents resource exhaustion
- **Health checks**: Liveness and readiness probes
- **TLS termination**: HTTPS encryption at route level

## Custom Domains

To use a custom domain:

1. **Update the route:**

```bash
oc patch route phone-selector -p '{"spec":{"host":"your-custom-domain.com"}}'
```

2. **Configure DNS** to point to your OpenShift router IP

## Cleanup

To remove the entire deployment:

```bash
# Using the script
./deploy-openshift.sh clean

# Manual cleanup
oc delete all -l app=phone-selector
oc delete configmap -l app=phone-selector
oc delete route -l app=phone-selector

# Delete the entire project
oc delete project phone-selector
```

## Support

For issues related to:

- **Application**: Check application logs and ensure all dependencies are correct
- **OpenShift**: Consult OpenShift documentation or contact your cluster administrator
- **Build failures**: Check build logs and ensure Dockerfile and dependencies are correct

## Advanced Configuration

### Using Persistent Storage

If you need persistent storage for data files:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: phone-selector-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

### Database Integration

For database connections, use OpenShift secrets:

```bash
oc create secret generic db-credentials \
  --from-literal=username=myuser \
  --from-literal=password=mypassword
```

### Custom Build Strategy

For more complex builds, modify the BuildConfig to use a custom builder image or multi-stage builds.

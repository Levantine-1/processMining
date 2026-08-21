# GitHub Actions assumes this role via OIDC (short-lived federated tokens)
# instead of a long-lived static IAM user key. The OIDC provider itself is
# account-wide and created once in the core terraform repo
# (iam/oidc/github_oidc_provider.tf) -- referenced here via a data source,
# never created per-repo (a second provider for the same issuer URL would
# collide).
data "aws_iam_openid_connect_provider" "github" {
  arn = "arn:aws:iam::975050308029:oidc-provider/token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Scoped to pushes to master specifically (this repo's actual default
    # branch), not a bare repo:* wildcard.
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:Levantine-1/processMining:ref:refs/heads/master"]
    }
  }
}

resource "aws_iam_role" "github_actions_processmining" {
  name               = "github_actions_processmining"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json
}

# ecr/ec2/route53 statements mirror the core repo's terraform/iam/policies/
# terraform_processmining_policy.tf (granted to the old static-key IAM
# user) -- kept self-contained here rather than referencing that module,
# since the point of this migration is per-repo terraform ownership. The
# s3 statements are new: that old policy never needed bucket access
# because Jenkins ran this repo's terraform against local state, not the
# shared S3 backend this migration moves it onto.
resource "aws_iam_role_policy" "github_actions_processmining_policy" {
  name = "github_actions_processmining_policy"
  role = aws_iam_role.github_actions_processmining.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:CreateRepository",
                "ecr:DeleteRepository",
                "ecr:DescribeRepositories",
                "ecr:PutImage",
                "ecr:BatchDeleteImage",
                "ecr:BatchGetImage",
                "ecr:DescribeImages",
                "ecr:GetDownloadUrlForLayer",
                "ecr:ListTagsForResource",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:BatchCheckLayerAvailability"
            ],
            "Resource": "arn:aws:ecr:${var.region}:975050308029:repository/processmining"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceTypes",
                "ec2:DescribeVolumes",
                "ec2:DescribeInstanceAttribute",
                "ec2:DescribeInstanceCreditSpecifications"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:GetHostedZone",
                "route53:ListTagsForResource",
                "route53:ChangeResourceRecordSets",
                "route53:GetChange",
                "route53:ListResourceRecordSets"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::prod-levantine-terraform-bucket/processMining/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::prod-levantine-terraform-bucket",
            "Condition": {
                "StringLike": {
                    "s3:prefix": "processMining/*"
                }
            }
        }
    ]
}
EOF
}

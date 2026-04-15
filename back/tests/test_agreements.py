"""Tests for agreements and signatures."""
import pytest
from app.models import Agreement, UserSignature


class TestAgreementManagement:
    """Tests for agreement creation and management."""

    def test_add_agreement_creates_agreement(self, db_session, platform):
        """Test that add_agreement creates an agreement."""
        agreement = platform.add_agreement(
            db_session,
            "Test Agreement",
            "Test description",
            "I agree to the terms."
        )
        
        assert agreement is not None
        assert isinstance(agreement, Agreement)
        assert agreement.name == "Test Agreement"
        assert agreement.description == "Test description"
        assert agreement.text == "I agree to the terms."

    def test_add_agreement_with_minimal_data(self, db_session, platform):
        """Test adding agreement with no description."""
        agreement = platform.add_agreement(
            db_session,
            "Minimal Agreement",
            None,
            "Terms."
        )
        
        assert agreement.description is None

    def test_add_agreement_unique_name(self, db_session, platform):
        """Test that agreement names must be unique."""
        platform.add_agreement(db_session, "Unique Agreement", None, "Terms")
        
        with pytest.raises(Exception):
            platform.add_agreement(db_session, "Unique Agreement", None, "Other terms")

    def test_get_agreement_text_by_id(self, db_session, platform, seeded_agreement):
        """Test retrieving agreement text by ID."""
        agreement = platform.get_agreement_text(db_session, seeded_agreement.id)
        assert agreement is not None
        assert agreement['name'] == "Test Agreement"

    def test_get_agreement_text_not_found(self, db_session, platform):
        """Test retrieving non-existent agreement returns None."""
        agreement = platform.get_agreement_text(db_session, 99999)
        assert agreement is None

    def test_get_agreements_for_user(self, db_session, platform, user_with_agreement):
        """Test getting agreements for a user."""
        agreements = platform.get_agreements_for_user(
            db_session, 
            user_with_agreement['session_id']
        )
        
        assert len(agreements) >= 1
        assert agreements[0]['agreement_id'] == user_with_agreement['agreement_id']

    def test_get_agreements_for_user_no_agreements(self, db_session, platform, test_user):
        """Test getting agreements for user with no agreements."""
        agreements = platform.get_agreements_for_user(db_session, test_user['session_id'])
        
        assert len(agreements) == 0


class TestAgreementSignatures:
    """Tests for user agreement signatures."""

    def test_record_agreement_creates_signature(self, db_session, platform, user_with_agreement):
        """Test that record_agreement creates a signature."""
        user_id = user_with_agreement['user_id']
        agreement_id = user_with_agreement['agreement_id']
        
        signature = db_session.query(UserSignature).filter(
            UserSignature.user_id == user_id,
            UserSignature.agreement_id == agreement_id
        ).one()
        
        assert signature is not None

    def test_record_agreement_multiple_times(self, db_session, platform, user_with_agreement):
        """Test recording same agreement multiple times."""
        user_id = user_with_agreement['user_id']
        agreement_id = user_with_agreement['agreement_id']
        
        # Record again
        result = platform.record_agreement(db_session, user_with_agreement['session_id'], agreement_id)
        
        signatures = db_session.query(UserSignature).filter(
            UserSignature.user_id == user_id,
            UserSignature.agreement_id == agreement_id
        ).all()
        
        # Should still have only one (idempotent)
        assert len(signatures) == 1

    def test_record_agreement_with_invalid_session(self, db_session, platform, seeded_agreement):
        """Test recording agreement with invalid session raises error."""
        with pytest.raises((ValueError, Exception)):
            platform.record_agreement(db_session, "invalid-session", seeded_agreement.id)

    def test_get_agreements_for_user_signed_status(self, db_session, platform, user_with_agreement):
        """Test that agreements show signed status."""
        agreements = platform.get_agreements_for_user(
            db_session, 
            user_with_agreement['session_id']
        )
        
        signed_agreement = next(
            (a for a in agreements if a['agreement_id'] == user_with_agreement['agreement_id']),
            None
        )
        
        assert signed_agreement is not None
        assert signed_agreement['signed_timestamp'] is not None

    def test_record_agreement_for_new_user(self, db_session, platform, seeded_agreement):
        """Test recording agreement creates user if needed."""
        # Use add_user to create a new user with session
        session_id, user_id = platform.add_user(db_session)
        
        # Record agreement
        result = platform.record_agreement(db_session, session_id, seeded_agreement.id)
        
        assert result is not None
        assert isinstance(result, UserSignature)
        assert result.agreement_id == seeded_agreement.id
        assert result.user_id == user_id

    def test_record_agreement_returns_existing(self, db_session, platform, user_with_agreement):
        """Test that recording existing agreement returns the existing signature."""
        agreement_id = user_with_agreement['agreement_id']
        session_id = user_with_agreement['session_id']
        
        # Record again
        result = platform.record_agreement(db_session, session_id, agreement_id)
        
        assert result is not None
        assert isinstance(result, UserSignature)
